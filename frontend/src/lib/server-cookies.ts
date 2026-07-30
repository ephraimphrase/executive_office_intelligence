// Server-only helper. Never import this from a Client Component or from
// lib/api.ts (which is shared with client code) — next/headers is only
// usable inside Server Components / Route Handlers / Server Actions.
import { cookies } from "next/headers";

/**
 * Reads the visiting browser's cookies from the incoming request (available
 * during SSR in a Server Component) and serializes them back into a `Cookie`
 * header string, so server-side data fetches can forward the user's session
 * to the backend the same way the browser would.
 */
export async function getServerCookieHeader(): Promise<string> {
  const cookieStore = await cookies();
  return cookieStore.toString();
}
