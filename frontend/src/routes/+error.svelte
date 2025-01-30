<script lang="ts">
  import { page } from "$app/state";
  import NotFound from "$lib/components/errors/NotFound.svelte";
  import Maintenance from "$lib/components/errors/Maintenance.svelte";
  import ServerError from "$lib/components/errors/ServerError.svelte";
  import UnknownServerError from "$lib/components/errors/UnknownServerError.svelte";

  const pages: { [key: number]: any } = {
    400: Maintenance,
    404: NotFound,
    500: ServerError,
  };

  const status = +page.status;
  const index = Object.keys(pages)
    .map((x) => +x)
    .reduce((p, c) => (p < status ? c : p));
  const component = pages[index] || UnknownServerError;
</script>

<svelte:component this={component}></svelte:component>
