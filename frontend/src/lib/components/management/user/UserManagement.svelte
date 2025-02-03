<script lang="ts">
  import { get, writable, type Writable } from "svelte/store";
  import { onDestroy, onMount } from "svelte";
  import Swal from "sweetalert2";
  import fastapi from "$lib/components/utils/fastapi.ts";
  import SignUp from "$lib/components/management/user/SignUp.svelte";
  import ChangePassword from "$lib/components/management/user/ChangePassword.svelte";

  type User = {
    user_id: string;
    role: string;
    created_at: string;
    is_locked: boolean;
  };

  interface FetchUserResult {
    users: User[];
    total: number;
  }

  let users: User[] = [];
  let searchQuery: string = "";
  let filterRole: string = "";
  let changePasswordID: string = "";
  let is_locked: boolean = false;
  const activeActionsUser: Writable<string> = writable("");
  const showCreateUser = writable(false);
  const showChangePassword = writable(false);

  // Pagination variables
  let currentPage = 1;
  let totalUsers = 0;
  let usersPerPage = 20;
  let totalPages = 1;

  function closeCreateModal() {
    showCreateUser.set(false);
    initialize_filter();
    fetchUsers(currentPage, usersPerPage);
  }

  function closeChangePasswordModal() {
    showChangePassword.set(false);
  }

  // handle actions
  const toggleActions = (userId: string) => {
    activeActionsUser.update((current) => (current === userId ? "" : userId));
  };

  const handleToggleLock = (user: User) => {
    if (user.is_locked) {
      handleUnlockUser(user.user_id);
    } else {
      handleLockUser(user.user_id);
    }
  };

  function initialize_filter() {
    is_locked = false;
    currentPage = 1;
    searchQuery = "";
    filterRole = "";
  }

  async function handleUnlockUser(userId: string) {
    try {
      const response = await new Promise<{
        user_id: string;
      }>((resolve, reject) => {
        fastapi("GET", "/session/id", {}, resolve, reject);
      });

      await new Promise<void>((resolve, reject) => {
        fastapi(
          "POST",
          `/user/unlock`,
          { user_id: userId, request_user: response.user_id },
          resolve,
          reject
        );
      });

      await fetchUsers(
        currentPage,
        usersPerPage,
        is_locked,
        searchQuery,
        filterRole
      );

      Swal.fire("성공", "계정이 성공적으로 활성화되었습니다.", "success");
    } catch (error: any) {
      Swal.fire(
        "오류",
        error.detail || "계정 활성화 중 문제가 발생했습니다.",
        "error"
      );
    }
  }

  async function handleLockUser(userId: string) {
    try {
      const response = await new Promise<{
        user_id: string;
      }>((resolve, reject) => {
        fastapi("GET", "/session/id", {}, resolve, reject);
      });

      await new Promise<void>((resolve, reject) => {
        fastapi(
          "POST",
          `/user/lock`,
          { user_id: userId, request_user: response.user_id },
          resolve,
          reject
        );
      });

      await fetchUsers(
        currentPage,
        usersPerPage,
        is_locked,
        searchQuery,
        filterRole
      );

      Swal.fire("성공", "계정이 성공적으로 비활성화되었습니다.", "success");
    } catch (error: any) {
      Swal.fire(
        "오류",
        error.detail || "계정 비활성화 중 문제가 발생했습니다.",
        "error"
      );
    }
  }

  async function handleDeleteUser(userId: string) {
    const result = await Swal.fire({
      title: "정말 이 계정을 삭제하시겠습니까?",
      text: "이 작업은 되돌릴 수 없습니다.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "확인",
      cancelButtonText: "취소",
    });

    if (result.isConfirmed) {
      try {
        const response = await new Promise<{
          user_id: string;
        }>((resolve, reject) => {
          fastapi("GET", "/session/id", {}, resolve, reject);
        });

        await new Promise<void>((resolve, reject) => {
          fastapi(
            "DELETE",
            `/user/`,
            { user_id: userId, request_user: response.user_id },
            resolve,
            reject
          );
        });

        initialize_filter();

        await fetchUsers(
          currentPage,
          usersPerPage,
          is_locked,
          searchQuery,
          filterRole
        );
        Swal.fire("성공", "계정이 성공적으로 삭제되었습니다.", "success");
      } catch (error: any) {
        Swal.fire(
          "오류",
          error.detail || "계정 삭제 중 오류가 발생했습니다.",
          "error"
        );
      }
    }
  }

  function changePasswordCliked() {
    changePasswordID = get(activeActionsUser);
    activeActionsUser.set("");
    showChangePassword.set(true);
  }

  // Pagination
  function changePage(page: number) {
    if (page > 0 && page <= totalPages) {
      currentPage = page;
      fetchUsers(currentPage, usersPerPage, is_locked, searchQuery, filterRole);
    }
  }

  function getPageNumbers() {
    const maxVisiblePages = 10;
    const pageNumbers = [];

    const groupStart =
      Math.floor((currentPage - 1) / maxVisiblePages) * maxVisiblePages + 1;
    const groupEnd = Math.min(groupStart + maxVisiblePages - 1, totalPages);

    for (let i = groupStart; i <= groupEnd; i++) {
      pageNumbers.push(i);
    }

    return pageNumbers;
  }

  async function fetchUsers(
    currentPage: number,
    usersPerPage: number,
    isLocked: boolean = false,
    searchQuery: string | null = null,
    filterRole: string | null = null
  ) {
    try {
      searchQuery = searchQuery || null;
      filterRole = filterRole || null;

      const result = await new Promise<FetchUserResult>((resolve, reject) => {
        fastapi(
          "GET",
          `/user/`,
          {
            page: currentPage,
            per_page: usersPerPage,
            is_locked: isLocked,
            user_id: searchQuery,
            role: filterRole,
          },
          resolve,
          reject
        );
      });

      users = result.users;
      totalUsers = result.total;
      totalPages = Math.max(1, Math.ceil(totalPages / usersPerPage));
    } catch (error) {
      if (error instanceof Error) {
        console.log(error.message);
      } else {
        console.log("An unknown error occurred");
      }
    }
  }

  function handleClickOutside(event: MouseEvent) {
    const activeActionsElement = document.getElementById(
      `actions-${$activeActionsUser}`
    );

    if (
      activeActionsElement &&
      !activeActionsElement.contains(event.target as Node)
    ) {
      activeActionsUser.set("");
    }
  }

  onMount(() => {
    fetchUsers(currentPage, usersPerPage);
    if (typeof window !== "undefined") {
      document.addEventListener("click", handleClickOutside);
    }
  });

  onDestroy(() => {
    if (typeof window !== "undefined") {
      document.removeEventListener("click", handleClickOutside);
    }
  });
</script>

<section
  class="flex flex-col w-full h-full items-center relative py-1 px-2 min-w-[650px]"
>
  <div class="h-full w-full p-4 flex flex-col">
    <div class="flex justify-between items-center w-full h-10 mb-3 select-none">
      <div
        class="flex items-center w-full h-full space-x-3 mr-3"
        style="min-width: 550px;"
      >
        <div class="relative w-96 h-full min-w-52">
          <div
            class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none"
          >
            <svg
              class="w-3 h-3 text-gray-500"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 20 20"
            >
              <path
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
              />
            </svg>
          </div>
          <input
            type="text"
            id="table-search"
            bind:value={searchQuery}
            class="block pl-8 w-full h-full text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50"
            placeholder="검색하려는 ID를 입력하세요"
          />
        </div>
        <select
          class="text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 h-full"
          bind:value={filterRole}
        >
          <option value="">전체</option>
          <option value="user">일반</option>
          <option value="admin">관리자</option>
        </select>
        <button
          class="text-white bg-blue-500 text-sm hover:bg-blue-700 py-1 h-full w-16 rounded-lg select-none"
          on:click={() => {
            currentPage = 1;
            fetchUsers(
              currentPage,
              usersPerPage,
              is_locked,
              searchQuery,
              filterRole
            );
          }}
        >
          검색
        </button>
        <div class="flex items-center space-x-1 justify-center h-full">
          <input
            type="checkbox"
            bind:checked={is_locked}
            on:change={() => {
              currentPage = 1;
              fetchUsers(
                currentPage,
                usersPerPage,
                is_locked,
                searchQuery,
                filterRole
              );
            }}
          />
          <p>비활성화 계정만 보기</p>
        </div>
      </div>
      <div class="h-full">
        <button
          class="text-white hover:bg-gray-100 flex justify-center items-center w-12 h-full rounded-lg text-sm select-none"
          on:click={() => {
            $showCreateUser = true;
          }}
          aria-label="Add user"
        >
          <svg
            class="w-9 h-9 text-gray-800 dark:text-white"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              fill-rule="evenodd"
              d="M9 4a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm-2 9a4 4 0 0 0-4 4v1a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-1a4 4 0 0 0-4-4H7Zm8-1a1 1 0 0 1 1-1h1v-1a1 1 0 1 1 2 0v1h1a1 1 0 1 1 0 2h-1v1a1 1 0 1 1-2 0v-1h-1a1 1 0 0 1-1-1Z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
    <table class="min-w-full table-fixed border border-gray-300 rounded-lg">
      <thead class="bg-gray-100 text-sm text-gray-700 uppercase">
        <tr>
          <th class="px-6 py-2.5 text-center" style="width: 25%;">아이디</th>
          <th class="px-6 py-2.5 text-center" style="width: 15%;">권한</th>
          <th class="px-6 py-2.5 text-center" style="width: 30%;">생성 시간</th>
          <th class="px-6 py-2.5 text-center" style="width: 20%;">상태</th>
          <th class="px-6 py-2.5 text-center" style="width: 10%;"></th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#if users.length === 0}
          <tr>
            <td colspan="5" class="text-center py-4 text-gray-500 text-sm">
              존재하는 사용자가 없습니다.
            </td>
          </tr>
        {:else}
          {#each users as user}
            <tr class="hover:bg-gray-50 text-center text-sm relative">
              <td class="px-6 py-2.5 text-gray-800" style="width: 25%;"
                >{user.user_id}</td
              >
              <td class="px-6 py-2.5 text-gray-800" style="width: 15%;"
                >{user.role === "user" ? "일반" : "관리자"}</td
              >
              <td class="px-6 py-2.5 text-gray-800" style="width: 30%;">
                {new Date(user.created_at).toLocaleString()}
              </td>
              <td class="px-6 py-2.5" style="width: 20%;">
                <span
                  class="px-2 py-1 text-xs rounded-lg text-white"
                  class:bg-green-500={user.is_locked === false}
                  class:bg-red-500={user.is_locked === true}
                >
                  {user.is_locked ? "비활성" : "활성"}
                </span>
              </td>
              <td class="px-6" style="width: 10%;">
                <button
                  class="text-gray-500 hover:text-gray-700 focus:outline-none"
                  on:click={(event) => {
                    event.stopPropagation();
                    toggleActions(user.user_id);
                  }}
                  aria-label="More options"
                >
                  <svg
                    class="w-8 h-8 text-gray-800"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke="currentColor"
                      stroke-linecap="round"
                      stroke-width="2"
                      d="M6 12h.01m6 0h.01m5.99 0h.01"
                    />
                  </svg>
                </button>
                {#if $activeActionsUser === user.user_id}
                  <div
                    id={`actions-${user.user_id}`}
                    class="absolute right-0 mt-0.5 bg-white border border-gray-300 rounded-lg shadow-lg z-10"
                    style="width: 140px;"
                  >
                    <button
                      class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                      on:click={() => handleToggleLock(user)}
                    >
                      {user.is_locked ? "계정 활성화" : "계정 비활성화"}
                    </button>
                    <button
                      class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                      on:click={() => handleDeleteUser(user.user_id)}
                    >
                      계정 삭제
                    </button>
                    <button
                      class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                      on:click={() => {
                        changePasswordCliked();
                      }}
                    >
                      비밀번호 변경
                    </button>
                  </div>
                {/if}
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>

    <div class="flex justify-center mt-4 space-x-2">
      <button
        class="px-3 py-1 border rounded disabled:opacity-50"
        on:click={() => changePage(currentPage - 1)}
        disabled={currentPage === 1}
      >
        &lt;
      </button>
      {#each getPageNumbers() as page}
        <button
          class="px-3 py-1 border rounded"
          class:font-bold={currentPage === page}
          on:click={() => changePage(page)}
        >
          {page}
        </button>
      {/each}
      <button
        class="px-3 py-1 border rounded disabled:opacity-50"
        on:click={() => changePage(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        &gt;
      </button>
    </div>
  </div>
  {#if $showCreateUser}
    <div
      class="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-20 h-full w-full min-h-[500px] min-w-[700px]"
    >
      <div class="min-h-[400px] min-w-[400px] bg-white rounded-lg shadow-lg">
        <SignUp onClose={closeCreateModal} />
      </div>
    </div>
  {/if}
  {#if $showChangePassword}
    <div
      class="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-20 h-full w-full min-h-[500px] min-w-[700px]"
    >
      <div class="min-h-[400px] min-w-[400px] bg-white rounded-lg shadow-lg">
        <ChangePassword
          onClose={closeChangePasswordModal}
          user_id={changePasswordID}
        />
      </div>
    </div>
  {/if}
</section>
