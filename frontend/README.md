# FilmFlow Studio - Frontend

Film Producer Decision Support Platform frontend built with React, TypeScript, and Tailwind CSS.

## Architecture Overview

This is a **React + Motoko** application running on the Internet Computer:

- **Frontend**: React with TypeScript, Tailwind CSS, and Shadcn UI components
- **Backend**: Motoko actor (single-actor pattern) running on Internet Computer
- **Storage**: Internet Computer canister storage (NOT PostgreSQL/Neon)

### Critical Architecture Rules

1. **Frontend NEVER accesses storage directly**
   - All data operations go through the Motoko backend actor
   - Use the hooks in `src/hooks/useQueries.ts` for all backend calls
   - DO NOT add database access logic to frontend code

2. **Single FilmProject Model**
   - All 8 phases update the SAME FilmProject model
   - DO NOT create separate schemas or data structures
   - The backend maintains one canonical data model

3. **Phase Independence**
   - Each phase (1-8) is independent and can be developed in parallel
   - Phase-specific logic should be added to individual phase pages
   - DO NOT modify core navigation or routing when adding phase features

## Project Structure

