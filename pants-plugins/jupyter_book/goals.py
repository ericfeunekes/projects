from dataclasses import dataclass
from pathlib import Path

from jupyter_book.target_types import DestinationBranchField, DirectoryField, JBTarget
from pants.backend.python.target_types import ConsoleScript
from pants.backend.python.util_rules.interpreter_constraints import (
    InterpreterConstraints,
)
from pants.backend.python.util_rules.pex import (
    Pex,
    PexProcess,
    PexRequest,
    PexRequirements,
)
from pants.engine.console import Console
from pants.engine.fs import Digest, DigestSubset, MergeDigests, PathGlobs, Workspace
from pants.engine.goal import Goal, GoalSubsystem
from pants.engine.process import ProcessResult
from pants.engine.rules import Get, MultiGet, collect_rules, goal_rule, rule
from pants.engine.target import Targets
from pants.option.option_types import ArgsListOption


class JupyterBook(GoalSubsystem):
    name = "jupyter-book"
    help = "Build jupyter-book documentation"

    args = ArgsListOption(example="build /docs")


class JupyterBookGoal(Goal):
    subsystem_cls = JupyterBook


@dataclass(frozen=True)
class JupyterBookDirectory:
    path: str
    target: JBTarget


@dataclass(frozen=True)
class BuildJupyterBook:
    path: str
    file_digest: Digest
    target: JBTarget


@rule
async def _build_jupyter_book(rule: JupyterBookDirectory) -> BuildJupyterBook:
    folder_digest = await Get(Digest, PathGlobs([f"{rule.path}/**"]))
    pex = await Get(
        Pex,
        PexRequest(
            output_filename="jupyter-book.pex",
            internal_only=True,
            requirements=PexRequirements(
                ["jupyter-book>=0.13.0", "sphinxcontrib-mermaid>=0.7.1"]
            ),
            interpreter_constraints=InterpreterConstraints(["CPython>=3.8"]),
            main=ConsoleScript("jupyter-book"),
        ),
    )
    digest = await Get(Digest, MergeDigests([folder_digest, pex.digest]))
    result = await Get(
        ProcessResult,
        PexProcess(
            pex,
            argv=["build", rule.path],
            description="Building a jupyter book",
            input_digest=digest,
            output_directories=[rule.path],
        ),
    )
    build_files = await Get(
        Digest, DigestSubset(result.output_digest, PathGlobs(["docs/_build/**"]))
    )
    return BuildJupyterBook(
        path=rule.path,
        file_digest=build_files,
        target=rule.target,
    )


@dataclass(frozen=True)
class GhPages:
    branch: str
    path: str
    input_digest: Digest


@dataclass(frozen=True)
class PushedToGithub:
    jupyter_cache: Digest


@rule
async def _push_to_gh_pages(pages: GhPages) -> PushedToGithub:
    jupyter_book_cache = Path(pages.path) / ".jupyter_cache"
    pex = await Get(
        Pex,
        PexRequest(
            output_filename="ghp-import.pex",
            internal_only=True,
            requirements=PexRequirements(["ghp-import>=2.1.0"]),
            interpreter_constraints=InterpreterConstraints(["CPython>=3.8"]),
            main=ConsoleScript("ghp-import"),
        ),
    )
    # Add the .git directory to a digest
    git_digest = await Get(Digest, PathGlobs([".git/**"]))
    # Merge the html digest with the git digest and the pex digest
    digest = await Get(
        Digest, MergeDigests([pages.input_digest, git_digest, pex.digest])
    )
    result = await Get(
        ProcessResult,
        PexProcess(
            pex,
            argv=["-n", "-p", "-f", "-b", pages.branch, pages.path],
            description="Pushing to github pages",
            input_digest=digest,
            output_directories=[jupyter_book_cache.as_posix()],
        ),
    )
    return PushedToGithub(jupyter_cache=result.output_digest)


@dataclass(frozen=True)
class PublishJB:
    target: JBTarget
    html_digest: Digest
    workspace: Workspace


@dataclass(frozen=True)
class Published:
    target: JBTarget


@rule
async def _publish_jupyter_book(publish: PublishJB) -> Published:
    target_branch = publish.target[DestinationBranchField].value

    if target_branch is None:
        publish.workspace.write_digest(publish.html_digest)
    else:
        await Get(
            PushedToGithub,
            GhPages(
                branch=target_branch,
                path=f"{publish.target[DirectoryField].value}/_build/html",
                input_digest=publish.html_digest,
            ),
        )

    return Published(target=publish.target)


@goal_rule
async def goal_jupyter_book(
    console: Console, workspace: Workspace, targets: Targets, jupyter_book: JupyterBook
) -> JupyterBookGoal:
    console.print_stdout("Building a jupyter book")
    jb_targets = [target for target in targets if isinstance(target, JBTarget)]
    builds = await MultiGet(
        Get(
            BuildJupyterBook,
            JupyterBookDirectory,
            JupyterBookDirectory(path=target[DirectoryField].value, target=target),
        )
        for target in jb_targets
    )
    await MultiGet(
        Get(
            Published,
            PublishJB,
            PublishJB(
                target=build.target, html_digest=build.file_digest, workspace=workspace
            ),
        )
        for build in builds
    )

    return JupyterBookGoal(exit_code=0)


def rules():
    return collect_rules()
