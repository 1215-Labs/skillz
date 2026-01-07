# LSP Type Safety Check Skill

## When to Use

When you need to verify type safety of code changes, especially before merge or deploy.

## Steps

1. Use **hover** on modified functions to extract parameter and return types
2. Use **find-references** to identify all callers
3. Use **hover** on call sites to verify type compatibility
4. Report any parameter/return type mismatches or unsafe call sites
