import { withAuth } from "@kinde-oss/kinde-auth-nextjs/middleware";

export default withAuth(
  async function middleware() {
  },
  {
    // middlware runs on all routes except the public paths (in this case the home page/index page)
    // the index page can be opened and viewed without sign in conditions ('/' -> index page)
    publicPaths:["/"]
  }
);

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
  ],
}