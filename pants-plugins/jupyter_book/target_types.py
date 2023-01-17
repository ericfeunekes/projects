from pants.engine.target import COMMON_TARGET_FIELDS, StringField, Target
from pants.option.subsystem import Subsystem


class DirectoryField(StringField):
    alias = "directory"
    help = "The directory to use for the book relative to the target's BUILD file."
    required = True


class DestinationBranchField(StringField):
    alias = "destination_branch"
    help = "The branch you want to publish the files to. If none, Then the current branch is used."
    required = False


class JBTarget(Target):
    alias = "jupyter_book_docs"
    core_fields = (*COMMON_TARGET_FIELDS, DirectoryField, DestinationBranchField)
    help = "A target to build jupyter-book documentation"


