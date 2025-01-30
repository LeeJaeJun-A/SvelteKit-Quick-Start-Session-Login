<script lang="ts">
  import fastapi from "$lib/components/utils/fastapi.ts";
  import { onMount } from "svelte";

  type UserLog = {
    user_id: string;
    action: string;
    success: string;
    error_code?: string;
    details?: string;
    log_timestamp: Date;
  };

  interface FetchLogResult {
    logs: UserLog[];
    total: number;
  }

  let today: string = new Date().toISOString().split("T")[0];

  let logs: UserLog[] = [];
  let filterUserID = "";
  let filterIsError: string = "";
  let filterStartDate = today;
  let filterEndDate = "";

  let currentPage = 1;
  let totalLogs = 0;
  let logsPerPage = 20;
  let totalPages = 1;

  async function fetchLogs(
    currentPage: number,
    logsPerPage: number,
    filterStartDate: string | null = null,
    filterEndDate: string | null = null,
    filterUserID: string | null = null,
    filterIsError: string | null = null
  ) {
    try {
      filterUserID = filterUserID || null;
      filterIsError = filterIsError || null;
      filterStartDate = filterStartDate || null;
      filterEndDate = filterEndDate || null;

      const result = await new Promise<FetchLogResult>((resolve, reject) => {
        fastapi(
          "GET",
          `/log/user`,
          {
            page: currentPage,
            per_page: logsPerPage,
            user_id: filterUserID,
            is_error: filterIsError,
            start_date: filterStartDate,
            end_date: filterEndDate,
          },
          resolve,
          reject
        );
      });

      logs = result.logs;
      totalLogs = result.total;
      totalPages = Math.max(1, Math.ceil(totalLogs / logsPerPage));

      console.log(logs);
    } catch (error) {
      if (error instanceof Error) {
        console.log(error.message);
      } else {
        console.log("An unknown error occurred");
      }
    }
  }

  function changePage(page: number) {
    if (page > 0 && page <= totalPages) {
      currentPage = page;
      fetchLogs(
        currentPage,
        logsPerPage,
        filterStartDate,
        filterEndDate,
        filterUserID,
        filterIsError
      );
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

  onMount(() => {
    fetchLogs(currentPage, logsPerPage, filterStartDate);
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
            class="block pl-8 w-full h-full text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50"
            bind:value={filterUserID}
            placeholder="검색하려는 ID를 입력하세요"
          />
        </div>
        <select
          class="text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 h-full"
          bind:value={filterIsError}
        >
          <option value="">전체</option>
          <option value="true">에러</option>
          <option value="false">성공</option>
        </select>
        <input
          type="date"
          class="text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 h-full"
          bind:value={filterStartDate}
        />
        <input
          type="date"
          class="text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 h-full"
          bind:value={filterEndDate}
        />
        <button
          class="text-white bg-blue-500 text-sm hover:bg-blue-700 py-1 h-full w-16 rounded-lg select-none"
          on:click={() => {
            currentPage = 1;
            fetchLogs(
              currentPage,
              logsPerPage,
              filterStartDate,
              filterEndDate,
              filterUserID,
              filterIsError
            );
          }}
        >
          검색
        </button>
      </div>
    </div>
    <table class="min-w-full table-fixed border border-gray-300 rounded-lg">
      <thead class="bg-gray-100 text-sm text-gray-700 uppercase">
        <tr>
          <th class="px-6 py-2.5 text-center" style="width: 10%;">아이디</th>
          <th class="px-6 py-2.5 text-center" style="width: 15%;">작업 종류</th>
          <th class="px-6 py-2.5 text-center" style="width: 5%;">성공 여부</th>
          <th class="px-6 py-2.5 text-center" style="width: 15%;">에러코드</th>
          <th class="px-6 py-2.5 text-center" style="width: 35%;">세부 사항</th>
          <th class="px-6 py-2.5 text-center" style="width: 20%;">로그 시간</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#if logs.length === 0}
          <tr>
            <td colspan="6" class="text-center py-4 text-gray-500 text-sm">
              해당하는 로그가 없습니다.
            </td>
          </tr>
        {:else}
          {#each logs as log}
            <tr class="hover:bg-gray-50 text-center text-sm relative">
              <td class="px-6 py-2.5 text-gray-800" style="width: 10%;"
                >{log.user_id}</td
              >
              <td class="px-6 py-2.5 text-gray-800" style="width: 15%;"
                >{log.action}</td
              >
              <td class="px-6 py-2.5" style="width: 5%;">
                <span
                  class="px-2 py-1 text-xs rounded-lg text-white"
                  class:bg-green-500={log.success === "True"}
                  class:bg-red-500={log.success === "False"}
                >
                  {log.success === "True" ? "성공" : "실패"}
                </span>
              </td>
              <td class="px-6 py-2.5 text-gray-800" style="width: 15%;"
                >{log.error_code ? log.error_code : "없음"}
              </td>
              <td class="px-6 py-2.5" style="width: 35%;">{log.details}</td>
              <td class="px-6 py-2.5" style="width: 20%;"
                >{log.log_timestamp}</td
              >
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
</section>
