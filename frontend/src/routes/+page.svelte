<!-- frontend/src/routes/+page.svelte  -->
<script lang="ts">
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import { goto } from "$app/navigation";
  import fastapi from "$lib/components/utils/fastapi.ts";

  onMount(async () => {
    if (browser) {
      const response = await new Promise<{
        role: string;
      }>((resolve, reject) => {
        fastapi("GET", "/session/role", {} , resolve, reject);
      });

      if (!response.role) {
        goto("/login", { replaceState: true });
      } else if (response.role === "admin") {
        goto("/setting", { replaceState: true });
      } else if (response.role === "user") {
        goto("/one", { replaceState: true });
      } else {
        // "/"을 첫 페이지로 할 때는 /one으로 가는 부분 다 수정
      }
    }
  });
</script>