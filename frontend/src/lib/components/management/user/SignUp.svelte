<script lang="ts">
  import Swal from "sweetalert2";
  import fastapi from "$lib/components/utils/fastapi.ts";
  import { EyeOutline, EyeSlashOutline } from "flowbite-svelte-icons";

  export let onClose;

  let showPassword = false;

  let user_id: string = "";
  let password: string = "";
  let role: string = "user";

  const handleSubmit = async (event: Event) => {
    event.preventDefault();

    const userData = { user_id, password, role };

    try {
      await new Promise((resolve, reject) => {
        fastapi("POST", "/user/", userData, resolve, reject);
      });

      Swal.fire("성공", "사용자가 성공적으로 생성되었습니다.", "success");
      onClose();
    } catch (error: any) {
      Swal.fire(
        "오류",
        error.detail || "사용자 생성 중 문제가 발생했습니다.",
        "error"
      );
    }
  };
</script>

<section
  class="bg-white rounded-lg p-8 flex flex-col justify-evenly items-center w-full h-full select-none"
>
  <span class="text-xl mb-6">계정 생성</span>
  <div class="w-full">
    <form
      on:submit|preventDefault={handleSubmit}
      class="w-full flex flex-col space-y-6"
    >
      <div>
        <label for="id" class="block text-xs font-medium text-gray-700"
          >아이디
        </label>
        <input
          id="id"
          type="text"
          bind:value={user_id}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
          required
        />
      </div>
      <div class="relative">
        <label for="password" class="block text-xs font-medium text-gray-700"
          >비밀번호</label
        >
        <input
          id="password"
          type={showPassword ? "text" : "password"}
          bind:value={password}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
          required
        />
        <button
          type="button"
          class="absolute inset-y-0 right-0 py-10 pr-3 flex items-center text-sm leading-5 h-full"
          on:click={() => {
            showPassword = !showPassword;
          }}
        >
          {#if showPassword}
            <EyeOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {:else}
            <EyeSlashOutline class="h-5 w-5 text-gray-500" aria-hidden="true" />
          {/if}
        </button>
      </div>
      <div>
        <label for="role" class="block text-xs font-medium text-gray-700"
          >역할</label
        >
        <select
          id="role"
          bind:value={role}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
        >
          <option value="user">일반</option>
          <option value="admin">관리자</option>
        </select>
      </div>
      <div class="flex space-x-8 items-center justify-center w-full pt-2">
        <button
          type="submit"
          class="flex w-16 h-8 justify-center items-center bg-blue-600 text-white text-sm rounded-md shadow-sm"
        >
          생성
        </button>
        <button
          type="button"
          on:click={onClose}
          class="flex w-16 h-8 justify-center items-center bg-gray-600 text-white text-sm rounded-md shadow-sm"
        >
          닫기
        </button>
      </div>
    </form>
  </div>
</section>
