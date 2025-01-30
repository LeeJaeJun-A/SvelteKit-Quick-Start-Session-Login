interface RoleMap {
  [key: string]: string[];
}

export let roleMap: RoleMap = {
  "/one": ["admin", "user"],
  "/two": ["admin", "user"],
  "/three": ["admin", "user"],
  "/settings": ["admin"],
};

export const protectedRoutes: string[] = [
  "/dashboards",
  "/detections",
  "/rules",
  "/settings",
];
