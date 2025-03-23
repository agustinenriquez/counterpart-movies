import { setupServer } from "msw/node";
import { http } from "msw";

const mockMoviesPage1 = {
  count: 4,
  next: "/api/movies/?page=2",
  previous: null,
  results: [
    {
      tconst: "tt001",
      title: "Movie B",
      original_title: "Movie B",
      year: "2022",
      runtime: "90",
      genre: "Comedy",
      rating: 4,
    },
    {
      tconst: "tt002",
      title: "Movie A",
      original_title: "Movie A",
      year: "2021",
      runtime: "95",
      genre: "Action",
      rating: 5,
    },
  ],
};

const mockMoviesPage2 = {
  count: 4,
  next: null,
  previous: "/api/movies/?page=1",
  results: [
    {
      tconst: "tt003",
      title: "Movie C",
      original_title: "Movie C",
      year: "2023",
      runtime: "100",
      genre: "Drama",
      rating: 3,
    },
    {
      tconst: "tt004",
      title: "Movie D",
      original_title: "Movie D",
      year: "2024",
      runtime: "110",
      genre: "Sci-Fi",
      rating: 4,
    },
  ],
};

const server = setupServer(
  http.get("http://127.0.0.1:8000/api/movies", ({ request }, res, ctx) => {
    const url = new URL(request.url);
    const page = url.searchParams.get("page") || "1";
    console.log("🔥 Intercepted:", url.href);

    const payload = page === "2" ? mockMoviesPage2 : mockMoviesPage1;
    return res(ctx.status(200), ctx.json(payload));
  })
);

beforeAll(() => {
  console.log("🚀 MSW Global Start...");
  server.listen({ onUnhandledRequest: "warn" });
});
afterEach(() => server.resetHandlers());
afterAll(() => {
  console.log("🛑 Stopping MSW...");
  server.close();
});
