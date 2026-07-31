# Issue tracker: GitHub

Issues and PRDs live in GitHub Issues for
`ReidSurmeier/editor-reidsurmeier-wtf`. Use the `gh` CLI.

## Conventions

- Create: `gh issue create --title "..." --body "..."`
- Read: `gh issue view <number> --comments`
- List: `gh issue list --state open`
- Comment: `gh issue comment <number> --body "..."`
- Apply or remove labels with `gh issue edit`.
- Close with `gh issue close`.

Never include credentials, private host material, original production image
inputs, or raw secret-scan findings in issues.

## Skill routing

When a skill says to publish to the issue tracker, create a GitHub issue. When
it says to fetch the relevant ticket, read the issue and its comments.
