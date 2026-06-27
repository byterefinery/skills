#!/usr/bin/env bun
// _vega-lite.js — Vega-Lite spec validator using AJV + local JSON schema
//
// Imports: ajv (resolved by bun at runtime)
// Usage:   bun _vega-lite.js validate [OPTIONS] <file|directory|->

import Ajv from "ajv";
import { stat, readdir } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// --- Load local schema ---
const __dirname = dirname(fileURLToPath(import.meta.url));
const schemaPath = join(__dirname, "vega-lite-schema.json");
const schema = JSON.parse(await Bun.file(schemaPath).text());

// --- AJV setup ---
// Add stub format validators so AJV doesn't warn about unknown formats
const ajv = new Ajv({
    allErrors: true,
    verbose: true,
    strict: false, // schema may use features that trigger strict warnings
});

// Register format stubs for formats the schema declares but we don't need to validate
for (const fmt of ["uri", "uri-reference", "color-hex"]) {
    ajv.addFormat(fmt, true); // true = accept any string
}

const validate = ajv.compile(schema);

// --- Color constants ---
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";
const RESET = "\x1b[0m";

// --- CLI helpers ---
function printUsage() {
    console.log(`
Usage: vega-lite.sh validate [OPTIONS] <file|directory|->

Validate Vega-Lite specifications against the official JSON schema (v6.4.3).

Options:
  -q, --quiet   Only output errors (suppress valid file markers)
  --json        Output results as JSON
  -h, --help    Show this help message

Arguments:
  <file>       Single .json, .vl.json, or .md file
  <directory>  Recursively validate all matching files
  -            Read a spec from stdin (JSON only)

Exit codes:
  0  All specs valid (or no vega-lite blocks found)
  1  One or more specs have validation errors
  2  Usage error`);
}

// --- Core validation ---

/**
 * Validate a single Vega-Lite spec (parsed JSON object).
 * Returns { valid: boolean, errors?: string[] }
 */
function validateSpec(spec) {
    validate(spec);
    if (validate.errors) {
        const messages = validate.errors.map((err) => {
            const path = err.instancePath || "/";
            const schemaPath = err.schemaPath.replace(/#\//, "").replace(/\//g, ".");
            return `  ${path} — ${err.message} (schema: ${schemaPath})`;
        });
        return { valid: false, errors: messages };
    }
    return { valid: true };
}

/**
 * Extract vega-lite code blocks from markdown content.
 * Returns array of { spec: object|null, rawCode: string, startLine: number, parseError?: string }
 */
function extractVegaLiteBlocks(content) {
    const blocks = [];
    const lines = content.split("\n");

    let inBlock = false;
    let blockStart = 0;
    let blockLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Match ```vega-lite (case-insensitive, optional whitespace)
        if (/^```[^\S\r\n]*vega-lite/i.test(line.trim())) {
            inBlock = true;
            blockStart = i + 1;
            blockLines = [];
        } else if (inBlock && line.trim() === "```") {
            inBlock = false;
            const rawCode = blockLines.join("\n").trim();
            let spec = null;
            let parseError = null;
            try {
                spec = JSON.parse(rawCode);
            } catch (e) {
                parseError = e instanceof Error ? e.message : String(e);
            }
            blocks.push({
                spec,
                rawCode,
                startLine: blockStart + 1, // 1-indexed
                parseError,
            });
        } else if (inBlock) {
            blockLines.push(line);
        }
    }

    return blocks;
}

/**
 * Validate all vega-lite blocks in a markdown file.
 */
async function validateMarkdownFile(filePath) {
    const content = await Bun.file(filePath).text();
    const blocks = extractVegaLiteBlocks(content);

    const results = [];
    for (let i = 0; i < blocks.length; i++) {
        const block = blocks[i];
        let result;

        if (block.parseError) {
            result = { valid: false, errors: [`JSON parse error: ${block.parseError}`] };
        } else {
            result = validateSpec(block.spec);
        }

        results.push({
            valid: result.valid,
            blockIndex: i + 1,
            errors: result.errors,
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
 * Validate a standalone .json / .vl.json file.
 */
async function validateJsonFile(filePath) {
    let content;
    try {
        content = await Bun.file(filePath).text();
    } catch {
        return {
            valid: false,
            blockIndex: 1,
            errors: ["Could not read file"],
            lineNumber: 1,
        };
    }

    let spec;
    try {
        spec = JSON.parse(content);
    } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return {
            valid: false,
            blockIndex: 1,
            errors: [`JSON parse error: ${msg}`],
            lineNumber: 1,
        };
    }

    const result = validateSpec(spec);
    return {
        valid: result.valid,
        blockIndex: 1,
        errors: result.errors,
        lineNumber: 1,
    };
}

// --- File system helpers ---

const MARKDOWN_EXTENSIONS = /\.(md|markdown|mdx)$/i;
const JSON_EXTENSIONS = /\.(json|vl\.json)$/i;
const MATCHING_EXTENSIONS = /\.(md|markdown|mdx|json|vl\.json)$/i;

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

// --- Output formatting ---

function formatErrors(errors, maxLines = 8) {
    if (!errors || errors.length === 0) return "";
    return errors.slice(0, maxLines).join("\n");
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
        let spec;
        try {
            spec = JSON.parse(stdin);
        } catch (e) {
            const msg = e instanceof Error ? e.message : String(e);
            if (jsonOutput) {
                console.log(JSON.stringify({ valid: false, errors: [`JSON parse error: ${msg}`] }, null, 2));
            } else {
                console.log(`${RED}Invalid${RESET}`);
                console.log(`JSON parse error: ${msg}`);
            }
            process.exit(1);
        }

        const result = validateSpec(spec);

        if (jsonOutput) {
            console.log(JSON.stringify({ valid: result.valid, errors: result.errors }, null, 2));
        } else if (result.valid) {
            console.log(`${GREEN}Valid${RESET}`);
        } else {
            console.log(`${RED}Invalid${RESET}`);
            console.log(formatErrors(result.errors));
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
    const allResults = [];

    for (const filePath of files) {
        if (MARKDOWN_EXTENSIONS.test(filePath)) {
            // Markdown file — extract vega-lite blocks
            const fileResult = await validateMarkdownFile(filePath);

            if (fileResult.totalBlocks === 0) {
                continue; // Skip files with no vega-lite blocks
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
                        const errorLines = formatErrors(block.errors).split("\n");
                        for (const line of errorLines) {
                            console.log(`  ${line}`);
                        }
                    }
                }

                allResults.push({
                    file: `${filePath}:block${block.blockIndex}`,
                    valid: block.valid,
                    errors: block.errors,
                });
            }

        } else if (JSON_EXTENSIONS.test(filePath)) {
            // JSON file — entire content is one spec
            const result = await validateJsonFile(filePath);

            if (result.valid) {
                totalValid++;
                if (!quiet && !jsonOutput) {
                    console.log(`${GREEN}✓${RESET} ${filePath}`);
                }
            } else {
                totalInvalid++;
                if (!jsonOutput) {
                    console.log(`${RED}✗${RESET} ${filePath}`);
                    const errorLines = formatErrors(result.errors).split("\n");
                    for (const line of errorLines) {
                        console.log(`  ${line}`);
                    }
                }
            }

            allResults.push({ file: filePath, valid: result.valid, errors: result.errors });

        } else {
            // Unknown extension — try as JSON first, then as markdown
            const content = await Bun.file(filePath).text();
            let spec;
            try {
                spec = JSON.parse(content);
                const result = validateSpec(spec);
                if (result.valid) {
                    totalValid++;
                    if (!quiet && !jsonOutput) {
                        console.log(`${GREEN}✓${RESET} ${filePath}`);
                    }
                } else {
                    totalInvalid++;
                    if (!jsonOutput) {
                        console.log(`${RED}✗${RESET} ${filePath}`);
                        const errorLines = formatErrors(result.errors).split("\n");
                        for (const line of errorLines) {
                            console.log(`  ${line}`);
                        }
                    }
                }
                allResults.push({ file: filePath, valid: result.valid, errors: result.errors });
            } catch {
                // Try as markdown with vega-lite blocks
                const blocks = extractVegaLiteBlocks(content);
                if (blocks.length === 0) {
                    continue;
                }

                for (let i = 0; i < blocks.length; i++) {
                    const block = blocks[i];
                    let result;
                    if (block.parseError) {
                        result = { valid: false, errors: [`JSON parse error: ${block.parseError}`] };
                    } else {
                        result = validateSpec(block.spec);
                    }

                    if (result.valid) {
                        totalValid++;
                        if (!quiet && !jsonOutput) {
                            console.log(`${GREEN}✓${RESET} ${filePath}:block${i + 1}`);
                        }
                    } else {
                        totalInvalid++;
                        if (!jsonOutput) {
                            console.log(
                                `${RED}✗${RESET} ${filePath}:block${i + 1} (line ${block.startLine})`
                            );
                            const errorLines = formatErrors(result.errors).split("\n");
                            for (const line of errorLines) {
                                console.log(`  ${line}`);
                            }
                        }
                    }

                    allResults.push({
                        file: `${filePath}:block${i + 1}`,
                        valid: result.valid,
                        errors: result.errors,
                    });
                }
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
        default:
            console.error(`${RED}Error: Unknown subcommand: ${subcommand}${RESET}`);
            printUsage();
            process.exit(2);
    }
}

main().catch((e) => {
    console.error(`${RED}Error: ${e.message}${RESET}`);
    process.exit(2);
});
