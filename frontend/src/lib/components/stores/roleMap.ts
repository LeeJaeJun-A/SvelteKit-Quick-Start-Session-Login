interface RoleMap {
  [key: string]: string[];
}

export let roleMap: RoleMap = {
  "/one": ["user"],
  "/two": ["user"],
  "/three": ["user"],
  "/settings": ["admin"],
};

export const protectedRoutes: string[] = ["/one", "/two", "/three", "/setting"];
