---
title: Talk to the library
description: How collaborators ask Claude, Cursor, ChatGPT, or Grok about FinancialLibrary records
audience: [general, educators]
topics: [resources, literacy]
status: published
last_reviewed: "2026-10-29"
---

# Talk to the library

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

You can ask an AI assistant to look up what this library already curated —
official consumer-education links, deposit-insurance explainers, and plain
vehicle pages — instead of hunting through folders yourself.

That works through a small local program called the **FinancialLibrary MCP
server** (`financial-library-mcp`). It only *reads* the records in this
repository. It never opens accounts, never sells products, and never turns a
lookup into personalized advice.

Prefer the public website when you just want to read:
[FinancialLibrary on GitHub Pages](https://ananddw24.github.io/safe_investment_researcher/).

## What you can ask

Phrase questions the way you would ask a librarian. Three useful starters:

1. **Emergency savings in India** —
   “What does FinancialLibrary say about emergency savings for households in
   India, and which official Indian sources should I open first?”
2. **What a training session covers** —
   “Summarize what Session 1 (emergency savings) covers in the community
   training materials, without recommending products.”
3. **Which official source to open** —
   “I need the official deposit-insurance page for the United States that this
   library curated — give me the title and the source URL only.”

If the assistant invents a product pitch or a target amount for your family,
stop and open the official `source_url` it cited (or browse the
[resource catalog](../resources/catalog.md) yourself).

## Before you connect anything

1. Clone or download this repository so the records sit on your computer.
2. Install the server once (needs Python and `pip`):

   ```bash
   cd safe_investment_researcher
   pip install ./mcp-server
   ```

3. Note the full path to that checkout. You will paste it as
   `FINANCIAL_LIBRARY_ROOT` in the steps below.

Technical install notes and tool names live in
[`mcp-server/README.md`](https://github.com/ananddw24/safe_investment_researcher/blob/main/mcp-server/README.md)
in the repository.

## Claude Desktop (works with this server)

Claude Desktop can run a **local** MCP server on your machine. That matches how
FinancialLibrary ships today (stdio only — no hosted URL yet).

1. Install [Claude Desktop](https://claude.ai/download) for your operating
   system.
2. Open the Claude Desktop config file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
3. Add (or merge) this block. Replace the path with *your* checkout:

   ```json
   {
     "mcpServers": {
       "financial-library": {
         "command": "financial-library-mcp",
         "env": {
           "FINANCIAL_LIBRARY_ROOT": "/path/to/safe_investment_researcher"
         }
       }
     }
   }
   ```

4. Fully quit and reopen Claude Desktop.
5. In a new chat, ask one of the [example questions](#what-you-can-ask). Claude
   should be able to use tools such as `search_records`, `get_record`, and
   `library_status`.

If the tools do not appear, confirm `financial-library-mcp` runs in a terminal
and that `FINANCIAL_LIBRARY_ROOT` points at the folder that contains `data/`.

## Cursor (short pointer)

Cursor can also attach this local server. Use the JSON block already documented
in
[`mcp-server/README.md`](https://github.com/ananddw24/safe_investment_researcher/blob/main/mcp-server/README.md)
(global `~/.cursor/mcp.json` or project `.cursor/mcp.json`), then restart
Cursor. Do not duplicate a second config here — keep that README as the single
install reference for editors.

## ChatGPT

The ChatGPT app **cannot attach this local stdio server as it ships today**.
ChatGPT’s custom MCP connections expect a remote HTTPS endpoint (or an OpenAI
Secure MCP Tunnel) on Business / Enterprise / Edu plans — not a plain
`financial-library-mcp` command on your laptop.

Closest working paths for collaborators: read the
[live website](https://ananddw24.github.io/safe_investment_researcher/), or use
**Claude Desktop** / **Cursor** with the steps above.

## Grok

The Grok app / [connectors](https://docs.x.ai/grok/connectors) page **cannot
attach this local stdio server as it ships today**. Custom Grok connectors need
a public HTTPS MCP URL; FinancialLibrary’s server does not expose one yet.

Closest working paths: the
[live website](https://ananddw24.github.io/safe_investment_researcher/), or
**Claude Desktop** / **Cursor**.

## Related

- [Guides index](index.md)
- [Using this library](../about/using-this-library.md)
- [Resource catalog](../resources/catalog.md)
- [Community training](../training/index.md)
- MCP server README:
  [`mcp-server/README.md`](https://github.com/ananddw24/safe_investment_researcher/blob/main/mcp-server/README.md)
