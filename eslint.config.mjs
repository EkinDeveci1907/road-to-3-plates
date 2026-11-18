// ESLint checks the app's script (copied out of index.html by tools/extract-js.py).
// Errors stop the pipeline: real bugs and dead code. Warnings are the code smells from class
// (complex methods, empty catch blocks): they show in the CI log but don't block a release.
import globals from "globals";

export default [
  {
    files: ["build/**/*.js"],
    languageOptions: { ecmaVersion: 2017, sourceType: "script", globals: { ...globals.browser } },
    rules: {
      "no-undef": "error",
      "no-unused-vars": ["error", { args: "none", caughtErrors: "none" }],
      "no-dupe-keys": "error",
      "no-unreachable": "error",
      "no-redeclare": "error",
      "no-self-assign": "error",
      "no-dupe-else-if": "error",
      "no-duplicate-case": "error",
      "no-loss-of-precision": "error",
      "no-empty": ["warn", { allowEmptyCatch: false }],
      "complexity": ["warn", 25],
    },
  },
];
