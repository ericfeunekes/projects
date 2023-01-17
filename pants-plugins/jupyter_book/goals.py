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
from pants.option.option_types import ArgsListOption, StrListOption

# Get logger for debugging and log to console
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class JupyterBook(GoalSubsystem):
    name = "jupyter-book"
    help = "Build jupyter-book documentation"
    default_version = "jupyter-book>=0.13.0"

    extra_requirements = StrListOption(
        default=[],
        help="Extra requirements to install when building the jupyter book",
        )

    args = ArgsListOption(
        passthrough=True,
        example="--builder html --toc toc.yml"
    )


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
async def _build_jupyter_book(rule: JupyterBookDirectory, jb: JupyterBook) -> BuildJupyterBook:
    folder_digest = await Get(Digest, PathGlobs([f"{rule.path}/**"]))
    jb_version = jb.default_version
    extra_requirements = jb.extra_requirements
    requirements = [jb_version] + list(extra_requirements)
    pex = await Get(
        Pex,
        PexRequest(
            output_filename="jupyter-book.pex",
            internal_only=True,
            requirements=PexRequirements(requirements),
            interpreter_constraints=InterpreterConstraints(["CPython>=3.8"]),
            main=ConsoleScript("jupyter-book"),
        ),
    )
    digest = await Get(Digest, MergeDigests([folder_digest, pex.digest]))
    logger.info(f"args: {jb.args}")
    result = await Get(
        ProcessResult,
        PexProcess(
            pex,
            argv=["build", rule.path, *list(jb.args)],
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
    logger.info(f"Git digest: {git_digest}")
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


@dataclass(frozen=True)
class Published:
    digest: Digest
    write_digest: bool


@rule
async def _publish_jupyter_book(publish: PublishJB) -> Published:
    target_branch = publish.target[DestinationBranchField].value
    if target_branch is None:
        logger.info("No target branch specified, skipping publishing to github pages")
        return Published(digest=publish.html_digest, write_digest=True)
    else:
        await Get(
            PushedToGithub,
            GhPages(
                branch=target_branch,
                path=f"{publish.target[DirectoryField].value}/_build/html",
                input_digest=publish.html_digest,
            ),
        )

    return Published(digest=publish.html_digest, write_digest=False)


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
    console.print_stdout("Publishing a jupyter book")
    results = await MultiGet(
        Get(
            Published,
            PublishJB,
            PublishJB(
                target=build.target, html_digest=build.file_digest
            ),
        )
        for build in builds
    )

    for result in results:
        if result.write_digest:
            workspace.write_digest(result.digest)
    return JupyterBookGoal(exit_code=0)


def rules():
    return collect_rules()
