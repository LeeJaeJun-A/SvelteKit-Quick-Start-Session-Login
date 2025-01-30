import { roleMap } from "$lib/components/stores/roleMap.ts";

export function getRequiredRoles(pathname: string): string[] | null {
  if (roleMap.hasOwnProperty(pathname)) {
    return roleMap[pathname];
  }

  const paths = Object.keys(roleMap);
  const matchingPath = paths.reduce((longest, path) => {
    if (pathname.startsWith(path) && path.length > longest.length) {
      return path;
    }
    return longest;
  }, "");

  return matchingPath ? roleMap[matchingPath] : null;
}

export function hasRequiredRoles(
  userRole: string,
  requiredRoles: string[]
): boolean {
  return requiredRoles.includes(userRole);
}

export function checkOnlyPageRouteRule(
  pageUrl: string,
  userRole: string
): boolean {
  const requiredRoles = getRequiredRoles(pageUrl);

  if (requiredRoles && !hasRequiredRoles(userRole, requiredRoles)) {
    return false;
  }

  return true;
}
