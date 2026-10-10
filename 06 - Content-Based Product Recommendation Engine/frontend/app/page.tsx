'use client';

import { FormEvent, useEffect, useState } from 'react';
import { ArrowRight, ExternalLink, Search, ShoppingBag, Sparkles, Star } from 'lucide-react';

type Product = {
  id: number; name: string; main_category: string; sub_category: string;
  image?: string | null; link?: string | null; ratings?: number | null;
  discount_price?: number | null; actual_price?: number | null; similarity_score?: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';
const demoProducts: Product[] = [
  { id: 1, name: 'Classic women’s cotton top', main_category: "Women's clothing", sub_category: 'Western wear', ratings: 4.4, discount_price: 699, actual_price: 1499, similarity_score: 0.94 },
  { id: 2, name: 'Relaxed fit solid casual top', main_category: "Women's clothing", sub_category: 'Western wear', ratings: 4.2, discount_price: 749, actual_price: 1699, similarity_score: 0.89 },
  { id: 3, name: 'Printed round neck everyday top', main_category: "Women's clothing", sub_category: 'Western wear', ratings: 4.1, discount_price: 599, actual_price: 1299, similarity_score: 0.85 },
];

function formatPrice(value?: number | null) {
  if (value == null) return 'Price unavailable';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);
}

export default function Home() {
  const [query, setQuery] = useState('women top');
  const [searchedFor, setSearchedFor] = useState('women top');
  const [products, setProducts] = useState<Product[]>(demoProducts);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('Preview results are shown until the FastAPI service is connected.');

  async function performSearch(rawQuery: string) {
    const trimmedQuery = rawQuery.trim();
    if (!trimmedQuery) throw new Error('Enter a product name');
    setLoading(true);
    setMessage('');
    try {
      const response = await fetch(`${API_URL}/api/recommendations?query=${encodeURIComponent(trimmedQuery)}&limit=8`);
      if (!response.ok) throw new Error('Search failed');
      const result = await response.json();
      setProducts(result.recommendations ?? []);
      setSearchedFor(result.selected_product?.name ?? trimmedQuery);
      setMessage(result.message ?? '');
    } catch {
      setProducts(demoProducts);
      setSearchedFor(trimmedQuery);
      setMessage('The recommendation service is offline, so sample results are displayed.');
      throw new Error('The recommendation service is offline');
    } finally {
      setLoading(false);
    }
  }

  async function searchProducts(event: FormEvent) {
    event.preventDefault();
    try {
      await performSearch(query);
    } catch {
      // The visible message already explains the failure.
    }
  }

  useEffect(() => {
    const context = (document as Document & {
      modelContext?: {
        registerTool: (tool: object, options?: { signal?: AbortSignal }) => void | Promise<void>;
      };
    }).modelContext;
    if (!context?.registerTool) return;

    const lifecycle = new AbortController();
    void Promise.resolve(context.registerTool({
      name: 'search_similar_products',
      title: 'Search similar products',
      description: 'Search the Acme catalogue and show FastText product recommendations.',
      inputSchema: {
        type: 'object',
        properties: { query: { type: 'string', minLength: 2 } },
        required: ['query'],
        additionalProperties: false,
      },
      annotations: { readOnlyHint: true, untrustedContentHint: true },
      execute: async (input: unknown) => {
        const candidate = input as { query?: unknown };
        if (typeof candidate.query !== 'string' || candidate.query.trim().length < 2) {
          throw new Error('Query must contain at least two characters');
        }
        setQuery(candidate.query);
        await performSearch(candidate.query);
        return { query: candidate.query, status: 'results_displayed' };
      },
    }, { signal: lifecycle.signal })).catch(() => undefined);

    return () => lifecycle.abort();
  }, []);

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border/80 bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-lg shadow-primary/20"><ShoppingBag size={20} /></span>
            <div><p className="text-lg font-bold tracking-tight">Acme Similar</p><p className="text-xs text-muted-foreground">FastText product discovery</p></div>
          </div>
          <span className="hidden items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 text-xs font-medium text-muted-foreground sm:flex"><span className="h-2 w-2 rounded-full bg-emerald-500" />70,000 products ready</span>
        </div>
      </header>

      <section className="relative overflow-hidden border-b border-border bg-hero">
        <div className="orb orb-one" /><div className="orb orb-two" />
        <div className="relative mx-auto max-w-7xl px-5 py-14 sm:px-8 sm:py-20">
          <div className="max-w-3xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1.5 text-sm font-semibold text-primary"><Sparkles size={15} /> Semantic recommendations</div>
            <h1 className="max-w-2xl text-4xl font-black leading-[1.05] tracking-[-0.04em] sm:text-6xl">Find products that feel like the one you love.</h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">Search any product name. FastText understands word patterns and returns the closest matches from the Acme Retail catalogue.</p>
            <form onSubmit={searchProducts} className="mt-8 flex max-w-2xl flex-col gap-3 rounded-3xl border border-border bg-card p-2 shadow-xl shadow-slate-900/8 sm:flex-row">
              <label className="flex min-w-0 flex-1 items-center gap-3 px-3" aria-label="Product name"><Search className="shrink-0 text-muted-foreground" size={21} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Try ‘running shoes’ or ‘women top’" className="h-12 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground/70" /></label>
              <button type="submit" disabled={loading} className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl bg-primary px-6 font-bold text-primary-foreground transition hover:-translate-y-0.5 hover:shadow-lg disabled:cursor-wait disabled:opacity-70">{loading ? 'Searching…' : 'Find similar'}{!loading && <ArrowRight size={18} />}</button>
            </form>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="mb-7 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div><p className="text-sm font-semibold uppercase tracking-[0.16em] text-primary">Closest matches</p><h2 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">Similar to “{searchedFor}”</h2></div>
          <p className="max-w-md text-sm text-muted-foreground">{message}</p>
        </div>
        {products.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-border bg-card p-12 text-center"><Search className="mx-auto text-muted-foreground" /><h3 className="mt-4 text-lg font-bold">No close matches found</h3><p className="mt-1 text-muted-foreground">Try a broader product name or category.</p></div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {products.map((product) => (
              <article key={`${product.id}-${product.name}`} className="group overflow-hidden rounded-3xl border border-border bg-card shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-900/8">
                <div className="relative grid aspect-[4/3] place-items-center overflow-hidden bg-product">
                  {product.image ? <img src={product.image} alt="" className="h-full w-full object-contain p-5 transition duration-300 group-hover:scale-105" /> : <ShoppingBag size={48} strokeWidth={1.25} className="text-primary/45" />}
                  {product.similarity_score != null && <span className="absolute right-3 top-3 rounded-full bg-slate-950/85 px-2.5 py-1 text-xs font-bold text-white backdrop-blur">{Math.round(product.similarity_score * 100)}% match</span>}
                </div>
                <div className="p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider text-primary">{product.sub_category}</p><h3 className="mt-2 min-h-12 line-clamp-2 font-bold leading-6">{product.name}</h3>
                  <div className="mt-3 flex items-center gap-2 text-sm">{product.ratings != null && <span className="inline-flex items-center gap-1 font-semibold"><Star size={15} className="fill-amber-400 text-amber-400" />{product.ratings}</span>}<span className="text-muted-foreground">{product.main_category}</span></div>
                  <div className="mt-5 flex items-end justify-between gap-3"><div><p className="text-lg font-black">{formatPrice(product.discount_price)}</p>{product.actual_price != null && <p className="text-xs text-muted-foreground line-through">{formatPrice(product.actual_price)}</p>}</div>{product.link && <a href={product.link} target="_blank" rel="noreferrer" aria-label={`Open ${product.name}`} className="grid h-10 w-10 place-items-center rounded-xl border border-border transition hover:border-primary hover:text-primary"><ExternalLink size={17} /></a>}</div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
