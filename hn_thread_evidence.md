# Hacker News thread evidence – Zig Error Patterns

**Thread:** https://news.ycombinator.com/item?id=44812985  
**Title:** Zig Error Patterns  
**Article:** https://glfmn.io/posts/zig-error-patterns/  
**Score:** 157  
**Descendants:** 53 comments  
**Fetched:** 2026-07-12 via HN Firebase API

## Access method

```bash
cd /usr/lib/node_modules/openclaw/dist/extensions/hackernews/skills/hackernews
python3 ./hackernews get-item --id 44812985
# recursive comment walk via Firebase API
```

Full structured data: [`hn_comments_sanitized.json`](hn_comments_sanitized.json) – 54 nodes (story + 53 comments), fields preserved: `id`, `type`, `by`, `time`, `parent`, `text`, `title`, `url`, `score`, `descendants`.

## Key commenters and positions

| Comment ID | Author | Parent | Summary |
|---|---|---|---|
| 44815545 | davidkunz | story | Asked about payload-less errors, `std.json` `UnexpectedToken` not helpful |
| 44816736 | quantummagic | 44815545 | Idiomatic: simple error + diagnostics out-param, no implicit alloc, "fundamental element of Zig's design" |
| 44822530 | nextaccountic | 44816736 | Caller must allocate space even if error unlikely |
| 44828073 | quantummagic | 44822530 | Out-param is optional; tradeoff favors correctness over convenience, OOM-safe reporting |
| 44818839 | metaltyphoon | 44816736 | "So… pretty much how C does it." |
| 44818975 | dwattttt | 44818839 | "Culture and coding standards count for a lot. C _can_ do this, but it's not normal to." |
| 44820807 | mark38848 | 44818975 | "It's still complete dogshit not to be able to have data there. Odin is much better here" |
| 44815908 | maleldil | 44815545 | `std.json` diagnostics object – "weakest part of Zig's error handling story" |
| 44816974 | AndyKelley | 44815908 | **Zig BDFL**: "`std.json` … is not a good example of proper error handling … painful and useless." / "`std.zon` author did not make this mistake" |
| 44817671 | AndyKelley | 44817264 | Links issue https://github.com/ziglang/zig/issues/1629 (std lib unification) |
| 44817144 | dnautics | 44815545 | "sneaky error payloads" article/video – compile-time, fully compiled out if unused |
| 44816301 | jmull | 44815545 | "errors are for control flow … return [other info] directly … or through an 'out' parameter" |
| 44825163 | meepmorp | 44816301 | …restating what Zig's BDFL said closing issue #2647 on error payloads |
| 44816131 | hansvm | 44815545 | Long analysis: try/catch/errdefer with payloads, Rust comparison, error type compatibility churn, `errdefer` is "the odd duck out", union return types, caller-specified return type |
| 44819842 | delifue | 44815256 | "Zig is elegant except for one thing: cannot attach data to error." – links #2647 |
| 44821107 | nektro | 44819842 | "attaching a payload requires asking … who and how the memory … is managed, and Zig … never prescribes you into a particular answer" |
| 44815081 | skrebbel | story | "Wow, errdefer sounds like the kind of thing every language ought to have." |

See `hn_comments_sanitized.json` for full comment text, timestamps, and threading.

## Related links mentioned in thread

- Linked article: https://glfmn.io/posts/zig-error-patterns/
- Error payloads issue: https://github.com/ziglang/zig/issues/2647
- Std lib unification: https://github.com/ziglang/zig/issues/1629
- "Sneaky error payloads": https://zig.news/ityonemo/sneaky-error-payloads-1aka
- Video: https://www.youtube.com/watch?v=aFeqWWJP4LE
- Zig language reference: https://ziglang.org/documentation/master/
- Zig stdlib docs: https://ziglang.org/documentation/master/std/
