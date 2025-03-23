import React, { useEffect, useState } from "react";
import axios from "axios";
import "./index.css";
import { Movie, Principal, Name, MoviesApiResponse } from "./types";
import { Film } from "lucide-react";

const PAGE_SIZE = 10;

const App: React.FC = () => {
  // State for movies, principals, names
  const [movies, setMovies] = useState<Movie[]>([]);
  const [principals, setPrincipals] = useState<Principal[]>([]);
  const [actorsForMovie, setActorsForMovie] = useState<{ [key: string]: string }>({});
  const [count, setCount] = useState<number>(0);

  const [moviesCache, setMoviesCache] = useState<{ [key: string]: Movie[] }>({});
  const [principalsCache, setPrincipalsCache] = useState<{ [key: string]: Principal[] }>({});
  const [actorsCache, setActorsCache] = useState<{ [key: string]: Name }>({});

  // State for pagination
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [prevPage, setPrevPage] = useState<string | null>(null);

  // Sorting state
  const [sortField, setSortField] = useState<string>("title");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // Selected movie for principals
  const [selectedMovie, setSelectedMovie] = useState<string | null>(null);

  const totalPages = Math.ceil(count / PAGE_SIZE);

  let rating = 0;

  // ⭐ Convert rating to stars
  const renderStars = (rating: number) => {
    if (!rating || rating < 0) return "No Rating"; // Handle missing or invalid ratings
    const stars = Math.round(rating.average_rating); // Round to nearest whole number
    return "⭐".repeat(stars); // Create star string
  };

  // 🔹 Fetch Movies with Sorting & Pagination
  useEffect(() => {
    const cacheKey = `page=${currentPage}&sort=${sortField}&order=${sortOrder}`;

    if (moviesCache[cacheKey]) {
      console.log("Using cached movies for:", cacheKey);
      const cached = moviesCache[cacheKey];
      setMovies(cached.results);
      setCount(cached.count);
      setNextPage(cached.next);
      setPrevPage(cached.previous);
      return;
    }

    const fetchMovies = async () => {
      try {
        console.log(`Fetching movies sorted by ${sortField} in ${sortOrder} order.`);
        setMovies([]); // Clear movie list before fetching new data

        const url = `/api/movies/?page=${currentPage}&sort=${sortField}&order=${sortOrder}`;
        const response = await axios.get<MoviesApiResponse>(url);

        setMovies(response.data.results);
        setCount(response.data.count);
        setNextPage(response.data.next);
        setPrevPage(response.data.previous);

        setMoviesCache((prev) => ({
          ...prev,
          [cacheKey]: response.data,
        }));
      } catch (err) {
        console.error("Failed to fetch movies:", err);
      }
    };

    fetchMovies();
  }, [currentPage, sortField, sortOrder]);

  // 🔹 Fetch Principals for the Selected Movie
  useEffect(() => {
    if (!selectedMovie) {
      setPrincipals([]);
      return;
    }

    if (principalsCache[selectedMovie]) {
      console.log("Using cached principals for:", selectedMovie);
      setPrincipals(principalsCache[selectedMovie]);
      return;
    }

    axios
      .get(`/api/principals/?tconst=${selectedMovie}`)
      .then((response) => {
        console.log("Fetched principals:", response.data);
        const fetchedPrincipals = response.data.results || response.data;
        setPrincipals(fetchedPrincipals);

        setPrincipalsCache((prev) => ({
          ...prev,
          [selectedMovie]: fetchedPrincipals,
        }));
      })
      .catch((err) => console.error("Failed to fetch principals:", err));
  }, [selectedMovie]);

  useEffect(() => {
    if (principals.length === 0) return;

    if (actorsCache[selectedMovie]) {
      console.log("Using cached actors for:", selectedMovie);
      setActorsForMovie((prev) => ({ ...prev, [selectedMovie]: actorsCache[selectedMovie].name }));
      return;
    }

    const nconsts = principals.map((p) => p.nconst);
    console.log("Fetching actors for:", nconsts);

    axios
      .get(`/api/names/?nconsts=${nconsts.join(",")}`)
      .then((response) => {
        console.log("Actor API Response:", response.data.results);

        const newActors = response.data.results.reduce((acc, actor) => {
          acc[actor.nconst] = actor.name;
          return acc;
        }, {} as { [key: string]: string });

        setActorsForMovie((prev) => ({ ...prev, ...newActors }));

        setActorsCache((prev) => ({
          ...prev,
          [selectedMovie]: newActors,
        }));
      })
      .catch((err) => console.error("Failed to fetch actor names:", err));
  }, [principals]);

  // 🔹 Set Random Movie
  const setRandomMovie = () => {
    // Get a random index from the movies array
    const randomIndex = Math.floor(Math.random() * movies.length);
    // Set the selected movie to the tconst of the random movie
    setSelectedMovie(movies[randomIndex].tconst);
  };

  // 🔹 Helper function to get actor names
  const getActorName = (nconst: string): string => {
    return actorsForMovie[nconst] || "Unknown Actor";
  };

  // 🔹 Toggle Sorting Order
  const toggleSortOrder = () => {
    setMovies([]); // Clear movies to force UI update
    setSortOrder((prevOrder) => (prevOrder === "asc" ? "desc" : "asc"));
    setCurrentPage(1); // Reset to first page
  };

  // 🔹 Pagination Handlers
  const handlePageClick = (page: number) => {
    setCurrentPage(page);
  };

  const [isDark, setIsDark] = useState<boolean>(() => {
    // Optionally persist theme using localStorage
    return localStorage.getItem("theme") === "dark";
  });

  const toggleDarkMode = () => {
    setIsDark((prev) => {
      const next = !prev;
      localStorage.setItem("theme", next ? "dark" : "light");

      // Apply class to <html> element
      if (next) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }

      return next;
    });
  };

  useEffect(() => {
    const isDarkStored = localStorage.getItem("theme") === "dark";
    if (isDarkStored) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    setIsDark(isDarkStored);
  }, []);


  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 dark:text-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4 shadow">
        <h1 className="text-3xl font-bold tracking-tight">🎬 Movie Explorer</h1>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Sorting Controls */}
        <div className="mb-4 flex items-center gap-4">
          <div>
            <label className="font-semibold mr-2">Sort by:</label>
            <select
                className="border p-1 rounded bg-white text-gray-800 dark:bg-gray-700 dark:text-white dark:border-gray-600"
              value={sortField}
              onChange={(e) => setSortField(e.target.value)}>
              <option value="title">Title</option>
              <option value="year">Year</option>
              <option value="genre">Genre</option>
              <option value="rating">Rating</option>
            </select>
          </div>
          <div>
            <label className="font-semibold mr-2">Order:</label>
            <button className="border px-2 py-1" onClick={toggleSortOrder}>
              {sortOrder === "asc" ? "Ascending" : "Descending"}
            </button>
          </div>
          <div>
            <button className="border px-2 py-1" onClick={() => setRandomMovie()}>
              Random Movie
            </button>
          </div>
          <button
          onClick={toggleDarkMode}
          className="ml-auto bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 border border-gray-300 dark:border-gray-600 px-3 py-1 rounded-md hover:shadow transition"
        >
          {isDark ? "☀️ Light Mode" : "🌙 Dark Mode"}
        </button>
        </div>
        <div className="grid sm:grid-cols-2 gap-6">
  {/* Movie List */}
  <div>
  <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-gray-100 transition-colors">
    Movies (Page {currentPage})</h2>

    <div className="grid gap-4">
      {Array.isArray(movies) && movies.map((movie) => (
        <div
          key={movie.tconst}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700
          shadow-sm rounded-lg p-4 cursor-pointer transition
          hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md"
          onClick={() => setSelectedMovie(movie.tconst)}
        >
          <h3 className="text-lg font-bold text-blue-700">{movie.title}</h3>
          <p className="text-sm text-gray-600">
            {movie.year} • {movie.genre || "Unknown Genre"}
          </p>
        </div>
      ))}
    </div>

    {/* Numbered Pagination Controls */}
    <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
      <button
        className={`px-3 py-1 rounded-md border text-sm ${
          !prevPage
            ? "bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-500"
            : "bg-white text-blue-600 hover:bg-blue-50 dark:bg-gray-700 dark:text-blue-300 dark:hover:bg-gray-600"
        }`}

        onClick={() => setCurrentPage(currentPage - 1)}
        disabled={!prevPage}
      >
        Prev
      </button>

      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
        <button
          key={page}
          className={`px-3 py-1 rounded-md border text-sm transition ${
            page === currentPage
              ? "bg-blue-600 text-white"
              : "bg-white text-blue-600 hover:bg-blue-50"
          }`}
          onClick={() => handlePageClick(page)}
        >
          {page}
        </button>
      ))}

      <button
        className={`px-3 py-1 rounded-md border text-sm ${
          !nextPage
            ? "bg-gray-100 text-gray-400 cursor-not-allowed"
            : "bg-white text-blue-600 hover:bg-blue-50"
        }`}
        onClick={() => setCurrentPage(currentPage + 1)}
        disabled={!nextPage}
      >
        Next
      </button>
    </div>
  </div>

{/* Principals for Selected Movie */}
{selectedMovie && (
  <div className="bg-white dark:bg-gray-800 dark:border-gray-700 rounded-xl border border-gray-200 shadow-sm p-6 transition-colors duration-300">
    <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
      <Film className="w-6 h-6 text-blue-500 dark:text-blue-300" />
      {movies.find((m) => m.tconst === selectedMovie)?.title}
    </h2>

    {sortField === "rating" && (
      <div className="mb-4">
        <span className="text-sm text-gray-600 dark:text-gray-300">Rating:</span>
        <div className="text-yellow-500 text-lg font-semibold mt-1">
          {renderStars(
            movies.find((m) => m.tconst === selectedMovie)?.rating || 0
          )}
        </div>
      </div>
    )}

    <div>
      <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-200 mb-2">Cast & Crew</h3>
        {Array.isArray(principals) && principals.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 italic">
            No principal data available.
          </p>
        ) : (
          <ul className="divide-y divide-gray-100 dark:divide-gray-700">
            {Array.isArray(principals) &&
              principals.map((p) => (
                <li key={p.id} className="py-2">
                  <p className="text-gray-800 dark:text-gray-100 text-sm">
                    <span className="font-medium">{getActorName(p.nconst)}</span>
                    <span className="text-gray-500 dark:text-gray-400"> — {p.category}</span>
                  </p>
                  {Array.isArray(p.characters) && p.characters.length > 0 && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 italic">
                      as {p.characters.join(", ")}
                    </p>
                  )}
                </li>
              ))}
          </ul>
        )}
    </div>
  </div>
)}


</div>


      </main>
    </div>
  );
};

export default App;
