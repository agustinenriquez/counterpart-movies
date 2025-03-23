import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";
import { setupServer } from "msw/node";
import { http } from "msw";

const server = setupServer(
  http.get("/api/movies/", (req, res, ctx) => {
    const parsedUrl = new URL(req.url.toString()); // ✅ this works in Node
    const page = parsedUrl.searchParams.get("page") || "1";

    if (page === "2") {
      return res(
        ctx.json({
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
        })
      );
    }

    return res(
      ctx.json({
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
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("App Component", () => {
  test("renders movie list", async () => {
    render(<App />);
    const movieA = await screen.findByText(/Movie A/i);
    const movieB = await screen.findByText(/Movie B/i);

    expect(movieA).toBeInTheDocument();
    expect(movieB).toBeInTheDocument();
  });

  test("sorts movies when sort order is changed", async () => {
    render(<App />);
    await screen.findByText(/Movie A/i);
    fireEvent.click(screen.getByText(/Ascending/i));
    const items = screen.getAllByRole("listitem");

    expect(items[0]).toHaveTextContent(/Movie A/i);
    expect(items[1]).toHaveTextContent(/Movie B/i);
  });

  test("paginates to the next page", async () => {
    render(<App />);
    expect(await screen.findByText(/Movie A/i)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Next/i));
    expect(await screen.findByText(/Movie C/i)).toBeInTheDocument();
    expect(screen.queryByText(/Movie A/i)).not.toBeInTheDocument();
  });
});
