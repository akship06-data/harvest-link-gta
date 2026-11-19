import React, { useEffect, useState } from 'react';
import { HeartHandshake, MapPin, ShieldCheck, Truck, UtensilsCrossed } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface Organization {
  id: number;
  name: string;
  org_type: 'donor' | 'pantry';
  neighborhood: string;
  address: string;
  has_refrigeration: boolean;
  accepted_dietary: string;
}

interface SurplusBatch {
  id: number;
  donor_id: number;
  matched_pantry_id: number | null;
  title: string;
  meal_count: number;
  storage_type: string;
  dietary_tags: string;
  expires_at: string;
  status: 'AVAILABLE' | 'CLAIMED' | 'PICKED_UP' | 'DELIVERED';
  volunteer_name: string | null;
}

interface PantryMatch {
  pantry_id: number;
  pantry_name: string;
  neighborhood: string;
  address: string;
  distance_km: number;
  compatibility_score: number;
  matched_tags: string[];
}

export default function App() {
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [batches, setBatches] = useState<SurplusBatch[]>([]);
  const [matchesByBatch, setMatchesByBatch] = useState<Record<number, PantryMatch[]>>({});
  const [volunteerName, setVolunteerName] = useState('Akshara P.');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [donorId, setDonorId] = useState<number>(1);
  const [title, setTitle] = useState('');
  const [mealCount, setMealCount] = useState(25);
  const [storageType, setStorageType] = useState<'refrigerated' | 'shelf_stable' | 'hot_held'>('refrigerated');
  const [dietaryTags, setDietaryTags] = useState('vegetarian, halal, nut_free');
  const [expiresInHours, setExpiresInHours] = useState(6);

  const fetchData = async () => {
    try {
      const [orgRes, batchRes] = await Promise.all([
        fetch(`${API_BASE}/organizations`),
        fetch(`${API_BASE}/batches`),
      ]);
      const orgData: Organization[] = await orgRes.json();
      const batchData: SurplusBatch[] = await batchRes.json();
      setOrgs(orgData);
      setBatches(batchData);

      const donors = orgData.filter((o) => o.org_type === 'donor');
      if (donors.length > 0 && !donors.some((d) => d.id === donorId)) {
        setDonorId(donors[0].id);
      }

      for (const b of batchData) {
        if (b.status === 'AVAILABLE') {
          const mRes = await fetch(`${API_BASE}/batches/${b.id}/matches`);
          const mData = await mRes.json();
          setMatchesByBatch((prev) => ({ ...prev, [b.id]: mData }));
        }
      }
    } catch {
      setErrorMsg('Backend API offline. Start FastAPI on http://localhost:8000 or check VITE_API_URL.');
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    const res = await fetch(`${API_BASE}/batches`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        donor_id: donorId,
        title,
        meal_count: Number(mealCount),
        storage_type: storageType,
        dietary_tags: dietaryTags.split(',').map((t) => t.trim()).filter(Boolean),
        expires_in_hours: Number(expiresInHours),
        sealed_commercial_source: true,
      }),
    });
    if (!res.ok) {
      const err = await res.json();
      setErrorMsg(err.detail?.[0]?.msg || err.detail || 'Validation failed.');
      return;
    }
    setTitle('');
    fetchData();
  };

  const handleClaim = async (batchId: number, pantryId: number) => {
    const res = await fetch(`${API_BASE}/batches/${batchId}/claim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pantry_id: pantryId, volunteer_name: volunteerName }),
    });
    if (res.ok) fetchData();
  };

  const handleAdvance = async (batchId: number) => {
    const res = await fetch(`${API_BASE}/batches/${batchId}/advance`, { method: 'POST' });
    if (res.ok) fetchData();
  };

  const donors = orgs.filter((o) => o.org_type === 'donor');
  const pantries = orgs.filter((o) => o.org_type === 'pantry');
  const totalMealsRescued = batches
    .filter((b) => b.status === 'DELIVERED')
    .reduce((acc, b) => acc + b.meal_count, 0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium">
              <MapPin className="w-4 h-4" />
              <span>Yonge–Dundas & Downtown Toronto Corridor</span>
            </div>
            <h1 className="text-2xl font-bold mt-1">HarvestLink GTA — Surplus Food Rescue Router</h1>
            <p className="text-slate-400 text-sm mt-1">
              Last-mile cold-chain & dietary matching between Dundas/TMU surplus donors and local drop-in pantries.
            </p>
          </div>
          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2.5 rounded-lg">
            <Truck className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-slate-400">Active Volunteer:</span>
            <input
              value={volunteerName}
              onChange={(e) => setVolunteerName(e.target.value)}
              className="bg-slate-800 text-sm px-2 py-1 rounded border border-slate-700 w-32 focus:outline-none"
            />
          </div>
        </header>

        {errorMsg && (
          <div className="bg-rose-950/60 border border-rose-700 text-rose-200 px-4 py-3 rounded-lg text-sm">
            {errorMsg}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-slate-400 text-xs uppercase tracking-wider">Meals Delivered</div>
            <div className="text-3xl font-bold text-emerald-400 mt-1">{totalMealsRescued}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-slate-400 text-xs uppercase tracking-wider">Active Surplus Batches</div>
            <div className="text-3xl font-bold text-sky-400 mt-1">
              {batches.filter((b) => b.status !== 'DELIVERED').length}
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="text-slate-400 text-xs uppercase tracking-wider">Verified Partner Sites</div>
            <div className="text-3xl font-bold text-amber-400 mt-1">{orgs.length}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <form onSubmit={handleCreateBatch} className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-4 h-fit">
            <div className="flex items-center gap-2 font-semibold text-lg">
              <UtensilsCrossed className="w-5 h-5 text-emerald-400" />
              <h2>Log Verified Food Surplus</h2>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">DineSafe-Verified Donor</label>
              <select
                value={donorId}
                onChange={(e) => setDonorId(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
              >
                {donors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.neighborhood})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Surplus Description</label>
              <input
                required
                placeholder="e.g., 30 Untouched Vegetarian Catering Boxes"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Est. Meals</label>
                <input
                  type="number"
                  min={1}
                  value={mealCount}
                  onChange={(e) => setMealCount(Number(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Safe Window (Hrs)</label>
                <input
                  type="number"
                  min={2}
                  step="0.5"
                  value={expiresInHours}
                  onChange={(e) => setExpiresInHours(Number(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Cold-Chain / Storage Type</label>
              <select
                value={storageType}
                onChange={(e) => setStorageType(e.target.value as any)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
              >
                <option value="refrigerated">Refrigerated Cold-Chain</option>
                <option value="shelf_stable">Sealed Shelf-Stable</option>
                <option value="hot_held">Hot-Held Commercial Catering</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Dietary Tags (comma-separated)</label>
              <input
                value={dietaryTags}
                onChange={(e) => setDietaryTags(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="flex items-start gap-2 text-xs text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>Protected under Ontario Donation of Food Act, 1994. Minimum 2-hour cold-chain window enforced.</span>
            </div>
            <button
              type="submit"
              className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold py-2.5 rounded-lg text-sm transition"
            >
              Publish Surplus & Match Pantries
            </button>
          </form>

          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-2 font-semibold text-lg">
              <HeartHandshake className="w-5 h-5 text-emerald-400" />
              <h2>Live Dundas & Downtown Dispatch Feed</h2>
            </div>

            {batches.map((batch) => {
              const donor = orgs.find((o) => o.id === batch.donor_id);
              const matchedPantry = pantries.find((p) => p.id === batch.matched_pantry_id);
              const candidateMatches = matchesByBatch[batch.id] || [];

              return (
                <div key={batch.id} className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-emerald-300">
                        {batch.status}
                      </span>
                      <h3 className="text-base font-semibold mt-1">{batch.title}</h3>
                      <p className="text-xs text-slate-400">
                        From {donor?.name} • {batch.meal_count} meals • {batch.storage_type}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {batch.dietary_tags.split(',').map((tag) => (
                        <span key={tag} className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  {batch.status === 'AVAILABLE' && (
                    <div className="border-t border-slate-800 pt-3 space-y-2">
                      <div className="text-xs font-medium text-slate-400">
                        Compatible Receiving Pantries (Ranked by Proximity & Cold-Chain):
                      </div>
                      {candidateMatches.map((m) => (
                        <div
                          key={m.pantry_id}
                          className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-slate-950 border border-slate-800 p-3 rounded-lg"
                        >
                          <div>
                            <div className="text-sm font-medium">{m.pantry_name}</div>
                            <div className="text-xs text-slate-400">
                              {m.address} • {m.distance_km} km away • Match Score: {m.compatibility_score}%
                            </div>
                          </div>
                          <button
                            onClick={() => handleClaim(batch.id, m.pantry_id)}
                            className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold px-3 py-1.5 rounded text-xs"
                          >
                            Claim Pickup
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {(batch.status === 'CLAIMED' || batch.status === 'PICKED_UP') && (
                    <div className="border-t border-slate-800 pt-3 flex flex-wrap items-center justify-between gap-2">
                      <div className="text-xs text-slate-300">
                        Courier: <span className="font-semibold">{batch.volunteer_name}</span> → Destination:{' '}
                        <span className="font-semibold">{matchedPantry?.name}</span>
                      </div>
                      <button
                        onClick={() => handleAdvance(batch.id)}
                        className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold px-3 py-1.5 rounded text-xs"
                      >
                        {batch.status === 'CLAIMED' ? 'Confirm Pickup & Temp Check' : 'Confirm Pantry Drop-Off'}
                      </button>
                    </div>
                  )}

                  {batch.status === 'DELIVERED' && (
                    <div className="border-t border-slate-800 pt-2 text-xs text-emerald-400">
                      Delivered to {matchedPantry?.name} by {batch.volunteer_name} (Chain-of-custody verified)
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
