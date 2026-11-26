#!/usr/bin/env bun
// _mermaid.js — Mermaid diagram validator using mermaid.parse() + DOM setup
//
// Imports: svgdom, jsdom, dompurify, mermaid (all resolved by bun at runtime)
// Usage:   bun _mermaid.js validate [OPTIONS] <file|directory|->

import { createHTMLWindow } from "svgdom";
import mermaidPkg from "mermaid";
import createDOMPurify from "dompurify";
import { JSDOM } from "jsdom";
import { stat, readdir } from "node:fs/promises";
import { join } from "node:path";

// --- Setup DOM environment (isomorphic-mermaid pattern) ---
const jsdomWindow = new JSDOM("").window;
const DOMPurify = createDOMPurify(jsdomWindow);
Object.assign(createDOMPurify, DOMPurify);

const svgWindow = createHTMLWindow();
Object.assign(globalThis, { window: svgWindow, document: svgWindow.document });

const mermaid = mermaidPkg.default || mermaidPkg;
mermaid.initialize({ startOnLoad: false });

// --- Color constants ---
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const RESET = "\x1b[0m";

// --- CLI helpers ---
function printUsage() {
    console.log(`
Usage: mermaid.sh validate [OPTIONS] <file|directory|->

Validate Mermaid diagram syntax using the official mermaid parser.

Options:
  -q, --quiet   Only output errors (suppress valid file markers)
  --json        Output results as JSON
  -h, --help    Show this help message

Arguments:
  <file>       Single .md, .mmd, .markdown, .mdx, or .mermaid file
  <directory>  Recursively validate all matching files
  -            Read diagram code from stdin

Exit codes:
  0  All diagrams valid (or no mermaid blocks found)
  1  One or more diagrams have syntax errors
  2  Usage error`);
}

// --- Core validation ---

/**
 * Validate a single mermaid diagram string.
 * Returns { valid: boolean, error?: string }
 */
async function validateDiagram(code) {
    try {
        await mermaid.parse(code.trim());
        return { valid: true };
    } catch (e) {
        const message = e instanceof Error ? e.message : String(e);
        return { valid: false, error: message };
    }
}

/**
 * Extract mermaid code blocks from markdown content.
 * Returns array of { code: string, startLine: number }
 */
function extractMermaidBlocks(content) {
    const blocks = [];
    const lines = content.split("\n");

    let inBlock = false;
    let blockStart = 0;
    let blockLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Match ```mermaid or ```  mermaid (with optional language hint)
        if (/^```[^\S\r\n]*mermaid/i.test(line.trim())) {
            inBlock = true;
            blockStart = i + 1;
            blockLines = [];
        } else if (inBlock && line.trim() === "```") {
            inBlock = false;
            blocks.push({
                code: blockLines.join("\n").trim(),
                startLine: blockStart + 1, // 1-indexed
            });
        } else if (inBlock) {
            blockLines.push(line);
        }
    }

    return blocks;
}

/**
 * Validate all mermaid blocks in a markdown file.
 */
async function validateMarkdownFile(filePath) {
    const content = await Bun.file(filePath).text();
    const blocks = extractMermaidBlocks(content);

    const results = [];
    for (let i = 0; i < blocks.length; i++) {
        const block = blocks[i];
        const result = await validateDiagram(block.code);

        results.push({
            valid: result.valid,
            blockIndex: i + 1,
            error: result.error,
            lineNumber: block.startLine,
        });
    }

    return {
        filePath,
        blocks: results,
        totalBlocks: blocks.length,
        validBlocks: results.filter((r) => r.valid).length,
        invalidBlocks: results.filter((r) => !r.valid).length,
    };
}

/**
 * Validate a standalone .mmd / .mermaid file (entire content is one diagram).
 */
async function validateMmdFile(filePath) {
    const content = await Bun.file(filePath).text();
    const result = await validateDiagram(content);

    return {
        valid: result.valid,
        blockIndex: 1,
        error: result.error,
        lineNumber: 1,
    };
}

// --- File system helpers ---

const MARKDOWN_EXTENSIONS = /\.(md|mmd|markdown|mdx|mermaid)$/i;
const STANDALONE_EXTENSIONS = /\.(mmd|mermaid)$/i;

/**
 * Find matching files in a directory recursively.
 */
async function findFiles(dir) {
    const results = [];

    async function scan(currentDir) {
        const entries = await readdir(currentDir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = join(currentDir, entry.name);
            if (entry.isDirectory()) {
                await scan(fullPath);
            } else if (MARKDOWN_EXTENSIONS.test(entry.name)) {
                results.push(fullPath);
            }
        }
    }

    await scan(dir);
    return results;
}

// --- Output formatting ---

function formatError(error, maxLines = 5) {
    if (!error) return "";
    return error.split("\n").slice(0, maxLines).join("\n");
}

// --- Main command handlers ---

async function cmdValidate(args) {
    let quiet = false;
    let jsonOutput = false;
    let input = null;

    for (const arg of args) {
        if (arg === "-h" || arg === "--help") {
            printUsage();
            process.exit(0);
        } else if (arg === "-q" || arg === "--quiet") {
            quiet = true;
        } else if (arg === "--json") {
            jsonOutput = true;
        } else if (arg === "-") {
            input = "-";
        } else if (arg.startsWith("-")) {
            console.error(`${RED}Error: Unknown option: ${arg}${RESET}`);
            printUsage();
            process.exit(2);
        } else {
            input = arg;
        }
    }

    if (!input) {
        console.error(`${RED}Error: No input specified. Provide a file, directory, or '-' for stdin.${RESET}`);
        printUsage();
        process.exit(2);
    }

    // --- Stdin mode ---
    if (input === "-") {
        const stdin = await Bun.stdin.text();
        const result = await validateDiagram(stdin);

        if (jsonOutput) {
            console.log(JSON.stringify({ valid: result.valid, error: result.error }, null, 2));
        } else if (result.valid) {
            console.log(`${GREEN}Valid${RESET}`);
        } else {
            console.log(`${RED}Invalid${RESET}`);
            console.log(formatError(result.error));
        }

        process.exit(result.valid ? 0 : 1);
    }

    // --- Check path exists and type ---
    let isDir = false;
    try {
        const statResult = await stat(input);
        isDir = statResult.isDirectory();
    } catch {
        console.error(`${RED}Error: Path does not exist: ${input}${RESET}`);
        process.exit(2);
    }

    let files = [];

    if (isDir) {
        files = (await findFiles(input)).sort();
    } else {
        files = [input];
    }

    if (files.length === 0) {
        if (jsonOutput) {
            console.log(JSON.stringify({ totalValid: 0, totalInvalid: 0, results: [] }, null, 2));
        } else {
            console.log(`${YELLOW}No markdown files found${RESET}`);
        }
        process.exit(0);
    }

    // --- Validate all files ---
    let totalValid = 0;
    let totalInvalid = 0;
    const allResults = [];

    for (const filePath of files) {
        const isStandalone = STANDALONE_EXTENSIONS.test(filePath);

        if (isStandalone) {
            const result = await validateMmdFile(filePath);

            if (result.valid) {
                totalValid++;
                if (!quiet && !jsonOutput) {
                    console.log(`${GREEN}✓${RESET} ${filePath}`);
                }
            } else {
                totalInvalid++;
                if (!jsonOutput) {
                    console.log(`${RED}✗${RESET} ${filePath}`);
                    const errorLines = formatError(result.error).split("\n");
                    for (const line of errorLines) {
                        console.log(`  ${line}`);
                    }
                }
            }

            allResults.push({ file: filePath, valid: result.valid, error: result.error });

        } else {
            const fileResult = await validateMarkdownFile(filePath);

            if (fileResult.totalBlocks === 0) {
                continue; // Skip files with no mermaid blocks
            }

            for (const block of fileResult.blocks) {
                if (block.valid) {
                    totalValid++;
                    if (!quiet && !jsonOutput) {
                        console.log(`${GREEN}✓${RESET} ${filePath}:block${block.blockIndex}`);
                    }
                } else {
                    totalInvalid++;
                    if (!jsonOutput) {
                        console.log(
                            `${RED}✗${RESET} ${filePath}:block${block.blockIndex} (line ${block.lineNumber})`
                        );
                        const errorLines = formatError(block.error).split("\n");
                        for (const line of errorLines) {
                            console.log(`  ${line}`);
                        }
                    }
                }

                allResults.push({
                    file: `${filePath}:block${block.blockIndex}`,
                    valid: block.valid,
                    error: block.error,
                });
            }
        }
    }

    // --- Output summary ---
    if (jsonOutput) {
        console.log(JSON.stringify({ totalValid, totalInvalid, results: allResults }, null, 2));
    } else {
        console.log("");
        console.log(
            `Summary: ${GREEN}${totalValid} valid${RESET}, ${totalInvalid > 0 ? RED : ""}${totalInvalid} invalid${RESET}`
        );
    }

    process.exit(totalInvalid > 0 ? 1 : 0);
}

// --- Render command (SVG/PNG) ---

function printRenderUsage() {
    console.log(`
Usage: mermaid.sh render [OPTIONS]

Convert a Mermaid diagram file to SVG or PNG using @mermaid-js/mermaid-cli.

Options:
  -i, --input <file>    Input file (.mmd, .mermaid, or .md with fenced mermaid blocks) [required]
  -o, --output <path>   Output file path (.svg or .png). Default: same name as input with .svg extension
  -t, --theme <name>    Theme: default, dark, forest, neutral, base (default: default)
  -w, --width <px>      Page width in pixels (default: 800)
  -H, --height <px>     Page height in pixels (default: 600)
  -s, --scale <number>  Canvas scale factor (default: 1)
  -c, --config <file>   Path to config file (mermaid-config.json or .json)
  -h, --help            Show this help message

Examples:
  mermaid.sh render -i diagram.mmd
  mermaid.sh render -i diagram.mmd -o output.png
  mermaid.sh render -i diagram.mmd -t dark -o output.svg
  mermaid.sh render -i notes.md -o output/
`);
}

async function cmdRender(args) {
    let output = null;
    let theme = "default";
    let width = 800;
    let height = 600;
    let scale = 1;
    let configFile = null;
    let input = null;

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === "-h" || arg === "--help") {
            printRenderUsage();
            process.exit(0);
        } else if (arg === "-i" || arg === "--input") {
            input = args[++i];
        } else if (arg === "-o" || arg === "--output") {
            output = args[++i];
        } else if (arg === "-t" || arg === "--theme") {
            theme = args[++i];
        } else if (arg === "-w" || arg === "--width") {
            width = parseInt(args[++i], 10);
        } else if (arg === "-H" || arg === "--height") {
            height = parseInt(args[++i], 10);
        } else if (arg === "-s" || arg === "--scale") {
            scale = parseFloat(args[++i]);
        } else if (arg === "-c" || arg === "--config") {
            configFile = args[++i];
        } else if (arg.startsWith("-")) {
            console.error(`${RED}Error: Unknown option: ${arg}${RESET}`);
            printRenderUsage();
            process.exit(2);
        } else {
            console.error(`${RED}Error: Unexpected positional argument: ${arg}${RESET}`);
            printRenderUsage();
            process.exit(2);
        }
    }

    if (!input) {
        console.error(`${RED}Error: No input file specified.${RESET}`);
        printRenderUsage();
        process.exit(2);
    }

    // Check input exists
    try {
        await stat(input);
    } catch {
        console.error(`${RED}Error: Input file does not exist: ${input}${RESET}`);
        process.exit(2);
    }

    // Build mmdc command args
    const mmdcArgs = [];
    mmdcArgs.push("-i", input);
    if (output) {
        mmdcArgs.push("-o", output);
    }
    mmdcArgs.push("-t", theme);
    mmdcArgs.push("-w", String(width));
    mmdcArgs.push("-H", String(height));
    mmdcArgs.push("-s", String(scale));
    if (configFile) {
        mmdcArgs.push("-c", configFile);
    }

    // Spawn bun x @mermaid-js/mermaid-cli with the args
    const proc = Bun.spawn(
        ["bun", "x", "@mermaid-js/mermaid-cli", ...mmdcArgs],
        {
            stdio: ["inherit", "inherit", "inherit"],
        }
    );

    const exitCode = await proc.exited;
    process.exit(exitCode);
}

// --- Main entry point ---
async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0 || args[0] === "-h" || args[0] === "--help") {
        console.log(`
Usage: mermaid.sh <subcommand> [OPTIONS]

Subcommands:
  validate    Validate Mermaid diagram syntax using the official parser
  render      Convert .mmd or .md files to SVG or PNG

Run 'mermaid.sh <subcommand> --help' for details on each subcommand.`);
        process.exit(0);
    }

    const subcommand = args[0];
    const subArgs = args.slice(1);

    switch (subcommand) {
        case "validate":
            await cmdValidate(subArgs);
            break;
        case "render":
            await cmdRender(subArgs);
            break;
        default:
            console.error(`${RED}Error: Unknown subcommand: ${subcommand}${RESET}`);
            console.log(`
Available subcommands: validate, render
Run 'mermaid.sh --help' for usage.`);
            process.exit(2);
    }
}

main().catch((e) => {
    console.error(`${RED}Error: ${e.message}${RESET}`);
    process.exit(2);
});
