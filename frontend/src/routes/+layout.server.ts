import { env } from "$env/dynamic/private";
import { redirect } from "@sveltejs/kit";
import Swal from "sweetalert2";
import { checkOnlyPageRouteRule } from "$lib/components/utils/roleRoutingChecker.ts";
import { protectedRoutes } from "$lib/components/stores/roleMap.ts";

export const load = async ({
  fetch,
  cookies,
  url,
}: {
  fetch: Function;
  cookies: any;
  url: URL;
}) => {
  const isLoginPage = url.pathname === "/login";
  const isProtected: boolean = protectedRoutes.some((route) =>
    url.pathname.startsWith(route)
  );
  const sessionID = cookies.get("session_id");

  if (isProtected && !sessionID && !isLoginPage) {
    throw redirect(302, "/login");
  }

  if (sessionID) {
    try {
      const baseUrl =
        env.PRIVATE_BACKEND_API_URL || "http://localhost:8000/api";

      await fetch(baseUrl + "/session", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Cookie: `session_id=${sessionID}`,
        },
        credentials: "include",
      });

      const response = await fetch(baseUrl + "/session/role", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Cookie: `session_id=${sessionID}`,
        },
        credentials: "include",
      });

      const data = await response.json();

      if (!checkOnlyPageRouteRule(url.pathname, data.role)) {
        throw redirect(302, "/forbidden");
      }
    } catch (error) {
      console.log(error);
      cookies.delete("session_id", {
        path: "/",
        domain: url.hostname,
        httpOnly: true,
        secure: false, // Change this value
      });

      if (!url.pathname.startsWith("/login")) {
        Swal.fire(
          "Error!",
          "Your session has expired or is unavailable.<br>Please login again."
        );
        throw redirect(302, "/login");
      }
    }
  }
};
