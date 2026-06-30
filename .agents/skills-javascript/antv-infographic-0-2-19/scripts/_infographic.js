#!/usr/bin/env bun
// _infographic.js — AntV Infographic syntax validator + SVG renderer
//
// Imports: @antv/infographic, @antv/infographic/ssr (resolved by bun at runtime)
// Usage:   bun _infographic.js <subcommand> [OPTIONS]

import { parseSyntax } from "@antv/infographic";
import { renderToString } from "@antv/infographic/ssr";
import { stat, readdir, mkdir } from "node:fs/promises";
import { join, dirname, basename, extname } from "node:path";

// --- Color constants ---
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";
const DIM = "\x1b[2m";
const RESET = "\x1b[0m";

// --- CLI helpers ---
function printUsage() {
    console.log(`
Usage: infographic.sh <subcommand> [OPTIONS]

Subcommands:
  validate    Validate infographic syntax using the official parser
  render      Convert infographic syntax to SVG (and optionally PNG)

Run 'infographic.sh <subcommand> --help' for details.`);
}

// --- Extract infographic blocks from markdown ---

/**
 * Extract infographic code blocks from markdown content.
 * Returns array of { code: string, startLine: number }
 */
function extractInfographicBlocks(content) {
    const blocks = [];
    const lines = content.split("\n");

    let inBlock = false;
    let blockStart = 0;
    let blockLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        // Check closing fence BEFORE opening fence
        if (inBlock && trimmed === "```") {
            inBlock = false;
            const rawCode = blockLines.join("\n").trim();
            if (rawCode.length > 0) {
                blocks.push({
                    code: rawCode,
                    startLine: blockStart + 1, // 1-indexed
                });
            }
        } else if (!inBlock && /^```[^\r\n]*infographic/i.test(trimmed)) {
            // Opening fence: ```infographic (case-insensitive)
            inBlock = true;
            blockStart = i + 1;
            blockLines = [];
        } else if (inBlock) {
            blockLines.push(line);
        }
    }

    return blocks;
}

// --- Core validation ---

/**
 * Validate a single infographic syntax string.
 * Returns { valid: boolean, errors: SyntaxError[], warnings: SyntaxError[], template?: string }
 */
function validateSyntax(code) {
    const result = parseSyntax(code.trim());
    return {
        valid: result.errors.length === 0,
        errors: result.errors,
        warnings: result.warnings,
        template: result.options.template,
    };
}

// --- Output formatting ---

function formatSyntaxError(err) {
    const codeLabel = err.code ? `[${err.code}]` : "";
    const path = err.path ? ` (${err.path})` : "";
    return `  Line ${err.line}${path}: ${err.message} ${codeLabel}`;
}

function formatWarning(warn) {
    const path = warn.path ? ` (${warn.path})` : "";
    return `  Line ${warn.line}${path}: ${warn.message}`;
}

// --- File system helpers ---

const MARKDOWN_EXTENSIONS = /\.(md|markdown|mdx)$/i;
const INFOGRAPHIC_EXTENSIONS = /\.(infographic|info)$/i;
const MATCHING_EXTENSIONS = /\.(md|markdown|mdx|infographic|info)$/i;

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
            } else if (MATCHING_EXTENSIONS.test(entry.name)) {
                results.push(fullPath);
            }
        }
    }

    await scan(dir);
    return results;
}

// --- Validate command ---

function printValidateUsage() {
    console.log(`
Usage: infographic.sh validate [OPTIONS] <file|directory|->

Validate infographic syntax using the official @antv/infographic parser.

Options:
  -q, --quiet   Only output errors (suppress valid file markers)
  --json        Output results as JSON
  -w, --warnings  Also show warnings (default: only errors)
  -h, --help    Show this help message

Arguments:
  <file>       Single .md, .markdown, .mdx, .infographic, or .info file
  <directory>  Recursively validate all matching files
  -            Read infographic syntax from stdin

Exit codes:
  0  All syntax valid (or no infographic blocks found)
  1  One or more syntax errors
  2  Usage error`);
}

async function cmdValidate(args) {
    let quiet = false;
    let jsonOutput = false;
    let showWarnings = false;
    let input = null;

    for (const arg of args) {
        if (arg === "-h" || arg === "--help") {
            printValidateUsage();
            process.exit(0);
        } else if (arg === "-q" || arg === "--quiet") {
            quiet = true;
        } else if (arg === "--json") {
            jsonOutput = true;
        } else if (arg === "-w" || arg === "--warnings") {
            showWarnings = true;
        } else if (arg === "-") {
            input = "-";
        } else if (arg.startsWith("-")) {
            console.error(`${RED}Error: Unknown option: ${arg}${RESET}`);
            printValidateUsage();
            process.exit(2);
        } else {
            input = arg;
        }
    }

    if (!input) {
        console.error(`${RED}Error: No input specified. Provide a file, directory, or '-' for stdin.${RESET}`);
        printValidateUsage();
        process.exit(2);
    }

    // --- Stdin mode ---
    if (input === "-") {
        const stdin = await Bun.stdin.text();
        const result = validateSyntax(stdin);

        if (jsonOutput) {
            console.log(JSON.stringify({ valid: result.valid, errors: result.errors, warnings: result.warnings }, null, 2));
        } else {
            if (result.errors.length > 0) {
                console.log(`${RED}Invalid${RESET}`);
                for (const err of result.errors) {
                    console.log(formatSyntaxError(err));
                }
            } else if (result.warnings.length > 0 && showWarnings) {
                console.log(`${YELLOW}Valid (with warnings)${RESET}`);
                for (const warn of result.warnings) {
                    console.log(formatWarning(warn));
                }
            } else {
                console.log(`${GREEN}Valid${RESET}`);
            }
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
            console.log(`${YELLOW}No matching files found${RESET}`);
        }
        process.exit(0);
    }

    // --- Validate all files ---
    let totalValid = 0;
    let totalInvalid = 0;
    let totalWarnings = 0;
    const allResults = [];

    for (const filePath of files) {
        if (MARKDOWN_EXTENSIONS.test(filePath)) {
            // Markdown file — extract infographic blocks
            const content = await Bun.file(filePath).text();
            const blocks = extractInfographicBlocks(content);

            if (blocks.length === 0) {
                continue;
            }

            for (let i = 0; i < blocks.length; i++) {
                const block = blocks[i];
                const result = validateSyntax(block.code);

                const hasWarnings = result.warnings.length > 0;

                if (result.valid) {
                    totalValid++;
                    if (hasWarnings) totalWarnings++;
                    if (!quiet && !jsonOutput) {
                        const warnLabel = hasWarnings ? ` ${YELLOW}(warnings)${RESET}` : "";
                        console.log(`${GREEN}✓${RESET} ${filePath}:block${i + 1}${warnLabel}`);
                    }
                } else {
                    totalInvalid++;
                    if (!jsonOutput) {
                        console.log(`${RED}✗${RESET} ${filePath}:block${i + 1} (line ${block.startLine})`);
                        for (const err of result.errors) {
                            console.log(formatSyntaxError(err));
                        }
                        if (showWarnings && result.warnings.length > 0) {
                            for (const warn of result.warnings) {
                                console.log(formatWarning(warn));
                            }
                        }
                    }
                }

                allResults.push({
                    file: `${filePath}:block${i + 1}`,
                    valid: result.valid,
                    errors: result.errors,
                    warnings: result.warnings,
                    template: result.template,
                });
            }

        } else if (INFOGRAPHIC_EXTENSIONS.test(filePath)) {
            // Standalone .infographic file — entire content is one spec
            const content = await Bun.file(filePath).text();
            const result = validateSyntax(content);

            const hasWarnings = result.warnings.length > 0;

            if (result.valid) {
                totalValid++;
                if (hasWarnings) totalWarnings++;
                if (!quiet && !jsonOutput) {
                    const warnLabel = hasWarnings ? ` ${YELLOW}(warnings)${RESET}` : "";
                    console.log(`${GREEN}✓${RESET} ${filePath}${warnLabel}`);
                }
            } else {
                totalInvalid++;
                if (!jsonOutput) {
                    console.log(`${RED}✗${RESET} ${filePath}`);
                    for (const err of result.errors) {
                        console.log(formatSyntaxError(err));
                    }
                    if (showWarnings && result.warnings.length > 0) {
                        for (const warn of result.warnings) {
                            console.log(formatWarning(warn));
                        }
                    }
                }
            }

            allResults.push({
                file: filePath,
                valid: result.valid,
                errors: result.errors,
                warnings: result.warnings,
                template: result.template,
            });

        } else {
            // Unknown extension — try as infographic, then as markdown
            const content = await Bun.file(filePath).text();
            const result = validateSyntax(content);

            if (result.errors.length === 0 || result.template) {
                // Looks like infographic syntax
                const hasWarnings = result.warnings.length > 0;
                if (result.valid) {
                    totalValid++;
                    if (hasWarnings) totalWarnings++;
                    if (!quiet && !jsonOutput) {
                        const warnLabel = hasWarnings ? ` ${YELLOW}(warnings)${RESET}` : "";
                        console.log(`${GREEN}✓${RESET} ${filePath}${warnLabel}`);
                    }
                } else {
                    totalInvalid++;
                    if (!jsonOutput) {
                        console.log(`${RED}✗${RESET} ${filePath}`);
                        for (const err of result.errors) {
                            console.log(formatSyntaxError(err));
                        }
                    }
                }
                allResults.push({
                    file: filePath,
                    valid: result.valid,
                    errors: result.errors,
                    warnings: result.warnings,
                    template: result.template,
                });
            } else {
                // Try as markdown with blocks
                const blocks = extractInfographicBlocks(content);
                if (blocks.length === 0) {
                    continue;
                }

                for (let i = 0; i < blocks.length; i++) {
                    const block = blocks[i];
                    const result = validateSyntax(block.code);

                    const hasWarnings = result.warnings.length > 0;

                    if (result.valid) {
                        totalValid++;
                        if (hasWarnings) totalWarnings++;
                        if (!quiet && !jsonOutput) {
                            const warnLabel = hasWarnings ? ` ${YELLOW}(warnings)${RESET}` : "";
                            console.log(`${GREEN}✓${RESET} ${filePath}:block${i + 1}${warnLabel}`);
                        }
                    } else {
                        totalInvalid++;
                        if (!jsonOutput) {
                            console.log(`${RED}✗${RESET} ${filePath}:block${i + 1} (line ${block.startLine})`);
                            for (const err of result.errors) {
                                console.log(formatSyntaxError(err));
                            }
                        }
                    }

                    allResults.push({
                        file: `${filePath}:block${i + 1}`,
                        valid: result.valid,
                        errors: result.errors,
                        warnings: result.warnings,
                        template: result.template,
                    });
                }
            }
        }
    }

    // --- Output summary ---
    if (jsonOutput) {
        console.log(JSON.stringify({ totalValid, totalInvalid, totalWarnings, results: allResults }, null, 2));
    } else {
        console.log("");
        console.log(
            `Summary: ${GREEN}${totalValid} valid${RESET}` +
            (totalWarnings > 0 ? `, ${YELLOW}${totalWarnings} with warnings${RESET}` : "") +
            `, ${totalInvalid > 0 ? RED : ""}${totalInvalid} invalid${RESET}`
        );
    }

    process.exit(totalInvalid > 0 ? 1 : 0);
}

// --- Render command ---

function printRenderUsage() {
    console.log(`
Usage: infographic.sh render [OPTIONS]

Convert infographic syntax to SVG (and optionally PNG).

Options:
  -i, --input <file>    Input file (.infographic, .info, or .md with fenced blocks) [required]
  -o, --output <path>   Output file path (.svg or .png). Default: same name as input with .svg extension
  -d, --dir <dir>       Output directory (used with -i for directories or multiple blocks)
  -b, --block <n>       Render only block N from markdown files (1-indexed, default: all)
  -w, --width <px>      SVG width (default: auto from template)
  -H, --height <px>     SVG height (default: auto from template)
  -h, --help            Show this help message

Examples:
  infographic.sh render -i chart.infographic
  infographic.sh render -i chart.infographic -o output.svg
  infographic.sh render -i notes.md -d ./output/
  infographic.sh render -i diagram.infographic -o diagram.png

Exit codes:
  0  Success
  1  Render error (syntax or rendering)
  2  Usage error`);
}

async function cmdRender(args) {
    let output = null;
    let outputDir = null;
    let blockIndex = null;
    let width = null;
    let height = null;
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
        } else if (arg === "-d" || arg === "--dir") {
            outputDir = args[++i];
        } else if (arg === "-b" || arg === "--block") {
            blockIndex = parseInt(args[++i], 10);
        } else if (arg === "-w" || arg === "--width") {
            width = parseInt(args[++i], 10);
        } else if (arg === "-H" || arg === "--height") {
            height = parseInt(args[++i], 10);
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
    let isDir = false;
    try {
        const statResult = await stat(input);
        isDir = statResult.isDirectory();
    } catch {
        console.error(`${RED}Error: Input file does not exist: ${input}${RESET}`);
        process.exit(2);
    }

    // Build init options
    const initOptions = {};
    if (width) initOptions.width = width;
    if (height) initOptions.height = height;

    // Collect input blocks
    const blocksToRender = [];

    if (isDir) {
        const files = (await findFiles(input)).sort();
        for (const filePath of files) {
            const content = await Bun.file(filePath).text();
            if (MARKDOWN_EXTENSIONS.test(filePath)) {
                const blocks = extractInfographicBlocks(content);
                for (let i = 0; i < blocks.length; i++) {
                    if (blockIndex !== null && i + 1 !== blockIndex) continue;
                    blocksToRender.push({
                        source: filePath,
                        code: blocks[i].code,
                        blockIndex: i + 1,
                    });
                }
            } else {
                blocksToRender.push({
                    source: filePath,
                    code: content,
                    blockIndex: 1,
                });
            }
        }
    } else {
        const content = await Bun.file(input).text();
        if (MARKDOWN_EXTENSIONS.test(input)) {
            const blocks = extractInfographicBlocks(content);
            for (let i = 0; i < blocks.length; i++) {
                if (blockIndex !== null && i + 1 !== blockIndex) continue;
                blocksToRender.push({
                    source: input,
                    code: blocks[i].code,
                    blockIndex: i + 1,
                });
            }
        } else {
            blocksToRender.push({
                source: input,
                code: content,
                blockIndex: 1,
            });
        }
    }

    if (blocksToRender.length === 0) {
        console.error(`${RED}Error: No infographic blocks found in input.${RESET}`);
        process.exit(1);
    }

    // Render each block
    let renderErrors = 0;
    let renderSuccess = 0;

    for (const block of blocksToRender) {
        // Validate first
        const validation = validateSyntax(block.code);
        if (!validation.valid) {
            console.log(`${RED}✗${RESET} ${block.source}${block.blockIndex > 1 ? `:block${block.blockIndex}` : ""} — syntax errors`);
            for (const err of validation.errors) {
                console.log(formatSyntaxError(err));
            }
            renderErrors++;
            continue;
        }

        // Determine output path
        let outputPath;
        if (output) {
            if (blocksToRender.length === 1) {
                outputPath = output;
            } else {
                // Generate name from source
                const base = basename(block.source, extname(block.source));
                const ext = extname(output) || ".svg";
                outputPath = join(dirname(output), `${base}-block${block.blockIndex}${ext}`);
            }
        } else if (outputDir) {
            const base = basename(block.source, extname(block.source));
            const name = block.blockIndex > 1 ? `${base}-block${block.blockIndex}` : base;
            outputPath = join(outputDir, `${name}.svg`);
            await mkdir(outputDir, { recursive: true });
        } else {
            const base = basename(block.source, extname(block.source));
            outputPath = `${base}.svg`;
        }

        // Ensure output directory exists
        await mkdir(dirname(outputPath), { recursive: true });

        try {
            const svg = await renderToString(block.code, Object.keys(initOptions).length > 0 ? initOptions : undefined);
            await Bun.write(outputPath, svg);
            renderSuccess++;
            console.log(`${GREEN}✓${RESET} ${block.source}${block.blockIndex > 1 ? `:block${block.blockIndex}` : ""} → ${outputPath}`);
        } catch (e) {
            renderErrors++;
            console.log(`${RED}✗${RESET} ${block.source}${block.blockIndex > 1 ? `:block${block.blockIndex}` : ""} — render error`);
            console.log(`  ${e.message}`);
        }
    }

    console.log("");
    console.log(
        `Rendered: ${GREEN}${renderSuccess} success${RESET}, ${renderErrors > 0 ? RED : ""}${renderErrors} failed${RESET}`
    );

    process.exit(renderErrors > 0 ? 1 : 0);
}

// --- Main entry point ---
async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0 || args[0] === "-h" || args[0] === "--help") {
        printUsage();
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
Run 'infographic.sh --help' for usage.`);
            process.exit(2);
    }
}

main().catch((e) => {
    console.error(`${RED}Error: ${e.message}${RESET}`);
    process.exit(2);
});
