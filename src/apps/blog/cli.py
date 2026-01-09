import argparse
from pathlib import Path
from dotenv import load_dotenv

from document_writer.apps.service import generate_document
from document_writer.domain.intent import load_intent_from_yaml
from document_writer.domain.editor import edit_document, make_editor_agent, AgentEditorRequest
from agentic_framework.agent_dispatcher import AgentDispatcherBase

from apps.blog.post import BlogPost
from apps.blog.storage import read_post_intent

load_dotenv(override=True)


POSTS_ROOT = Path("posts")


def main():
    parser = argparse.ArgumentParser(prog="blog")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate")
    gen.add_argument("--title", required=True)
    gen.add_argument("--author", required=True)
    gen.add_argument("--intent", required=True)
    gen.add_argument("--status", default="draft")

    edit = sub.add_parser("edit")
    edit.add_argument("--post-id", required=True)
    edit.add_argument("--policy", required=True)
    edit.add_argument("--base-revision", type=int, default=None)

    args = parser.parse_args()

    if args.cmd == "generate":
        generate(args)
    elif args.cmd == "edit":
        edit_post(args)


# ---------- generate ----------

def generate(args):
    intent = load_intent_from_yaml(Path(args.intent).read_text())

    result = generate_document(
        intent=intent,
        trace=False,
    )

    post = BlogPost(
        title=args.title,
        author=args.author,
        intent=intent.model_dump(),
        content=result.markdown,
        status=args.status,
    )

    path = post.persist()
    print(f"Blog post created at: {path}")


# ---------- edit ----------

def edit_post(args):
    post_dir = POSTS_ROOT / args.post_id
    if not post_dir.exists():
        raise FileNotFoundError(f"Post not found: {post_dir}")

    content_path = post_dir / "content.md"
    revisions_dir = post_dir / "revisions"
    revisions_dir.mkdir(exist_ok=True)

    # load base content
    if args.base_revision is not None:
        base_file = revisions_dir / f"{args.base_revision:03d}.md"
        if not base_file.exists():
            raise FileNotFoundError(f"Revision not found: {base_file}")
        document = base_file.read_text()
    else:
        document = content_path.read_text()

    editing_policy = Path(args.policy).read_text()
    intent = read_post_intent(args.post_id)

    # archive current content
    existing = sorted(revisions_dir.glob("*.md"))
    next_rev = len(existing) + 1
    revisions_dir.joinpath(f"{next_rev:03d}.md").write_text(document)

    # run editor
    agent = make_editor_agent()
    dispatcher = AgentDispatcherBase()

    response = edit_document(
        AgentEditorRequest(
            document=document,
            editing_policy=editing_policy,
            intent=intent,
        ),
        dispatcher=dispatcher,
        editor_agent=agent,
    )

    content_path.write_text(response.edited_document)

    print(f"Post edited: {args.post_id}")
    print(f"New revision: {next_rev:03d}")


if __name__ == "__main__":
    main()
