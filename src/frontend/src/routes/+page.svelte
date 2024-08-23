<script>
  let story_id = "";
  let credentials = {
    username: "",
    password: "",
  };
  let after_download_page = false;
  let url = "";

  let raw_story_id = "";

  let button_disabled = false;
  $: button_disabled = !(
    story_id &&
    credentials.username &&
    credentials.password
  );

  $: url = `/download/${story_id}?om=1&username=${encodeURIComponent(credentials.username)}&password=${encodeURIComponent(credentials.password)}`;

  $: {
    raw_story_id = raw_story_id.toLowerCase();
    if (raw_story_id.includes("inkitt.com/stories")) {
      story_id = raw_story_id.split("/stories/")[1].split("/")[1].split("?")[0];
    } else {
      story_id = parseInt(raw_story_id) || ""; // parseInt returns NaN for undefined values.
      raw_story_id = story_id;
    }
    raw_story_id = story_id;
  }

  function reset() {
    after_download_page = false;
    story_id = "";
    raw_story_id = "";
  }
</script>

<div>
  <div class="hero min-h-screen">
    <div
      class="hero-content flex-col lg:flex-row-reverse bg-base-100/50 p-16 rounded shadow-sm"
    >
      {#if !after_download_page}
        <div class="text-center lg:text-left lg:p-10">
          <h1
            class="font-extrabold text-transparent text-5xl bg-clip-text bg-gradient-to-r to-purple-600 via-black-600 from-blue-700"
          >
            Inkitt Downloader
          </h1>
          <p class="pt-6 text-lg">
            Download your favourite books with a single click!
          </p>
        </div>
        <div class="card shrink-0 w-full max-w-sm shadow-2xl bg-base-100">
          <form class="card-body">
            <div class="form-control">
              <input
                type="text"
                placeholder="Story ID"
                class="input input-bordered"
                bind:value={raw_story_id}
                required
                name="story_id"
              />
              <label class="label" for="story_id">
                <button
                  class="label-text link font-semibold"
                  onclick="StoryIDTutorialModal.showModal()"
                  data-umami-event="StoryIDTutorialModal Open"
                  >How to get a Story ID</button
                >
              </label>
              <label class="input input-bordered flex items-center gap-2">
                Username
                <input
                  type="text"
                  class="grow"
                  name="username"
                  placeholder="foxtail.chicken"
                  bind:value={credentials.username}
                  required
                />
              </label>
              <label class="input input-bordered flex items-center gap-2">
                Password
                <input
                  type="password"
                  class="grow"
                  placeholder="supersecretpassword"
                  name="password"
                  bind:value={credentials.password}
                  required
                />
              </label>
            </div>

            <div class="form-control mt-6">
              <a
                class="btn btn-primary rounded-l-none"
                class:btn-disabled={button_disabled}
                data-umami-event="Download"
                href={url}
                on:click={() => (after_download_page = true)}>Download</a
              >
            </div>
          </form>
        </div>
      {:else}
        <div class="text-center max-w-4xl">
          <h1 class="font-bold text-3xl">
            Your download has <span
              class="text-transparent bg-clip-text bg-gradient-to-r to-purple-600 via-black-600 from-blue-700"
              >Started</span
            >
          </h1>
          <div class="py-4 space-y-2">
            <p class="text-2xl">
              If you found this site useful, please consider <a
                href="https://github.com/AaronBenDaniel/InkittDownloader"
                target="_blank"
                class="link"
                data-umami-event="Star">starring the project</a
              > to support InkittDownloader.
            </p>
            <!-- <p class="text-lg pt-2">
              You can also join us on <a
                href="https://discord.gg/P9RHC4KCwd"
                target="_blank"
                class="link"
                data-umami-event="Discord">discord</a
              >, where we release features early and discuss updates.
            </p> -->
          </div>
          <a on:click={() => reset()} class="btn btn-outline btn-lg mt-10"
            >Download More</a
          >
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Open the modal using ID.showModal() method -->

<dialog id="StoryIDTutorialModal" class="modal">
  <div class="modal-box">
    <form method="dialog">
      <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2"
        >✕</button
      >
    </form>
    <h3 class="font-bold text-lg">Retrieving a Story ID</h3>
    <ol class="list list-disc list-inside py-4 space-y-4">
      <li>
        Open the Story URL, this page includes the story description and tags.
        (For example, <span class="font-mono bg-slate-100 p-1"
          >wattpad.com/story/237369078-wattpad-books-presents</span
        >).
      </li>
      <li>
        Copy the numbers after the <span class="font-mono bg-slate-100 p-1"
          >/</span
        >
        (In the example, that'd be,
        <span class="font-mono bg-slate-100 p-1"
          >wattpad.com/story/<span class="bg-amber-200 p-1">237369078</span
          >-wattpad-books-presents</span
        >)
      </li>
      <li>Paste the Story ID and hit Download!</li>
    </ol>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
