import { defineCollection, z } from 'astro:content';
import { file } from 'astro/loaders';

const Evidence = z.object({
  field: z.string(),
  url: z.string(),
  source_type: z.enum(['literature', 'news', 'hub', 'official']),
  fetched: z.string(),
  sha256: z.string().nullable().optional(),
  note: z.string().optional(),
});

const models = defineCollection({
  loader: file('src/content/generated/models.json'),
  schema: z.object({
    id: z.string(), name: z.string(), org: z.string(),
    release_date: z.string().nullable(), params_b: z.number().nullable(),
    arch_type: z.string().nullable(), arch_notes: z.string().nullable().optional(),
    license: z.string().nullable(), commercial_ok: z.boolean().nullable(),
    weights_url: z.string().nullable(), code_url: z.string().nullable(), paper_url: z.string().nullable(),
    modalities_in: z.array(z.string()), action_space: z.string().nullable(),
    cross_embodiment: z.string().nullable(), pretrain_hours: z.number().nullable(),
    target_embodiments: z.array(z.string()), evidence: z.array(Evidence),
  }),
});

const embodiments = defineCollection({
  loader: file('src/content/generated/embodiments.json'),
  schema: z.object({
    id: z.string(), name: z.string(), vendor: z.string(), form: z.string(),
    dof: z.number().nullable(), end_effector: z.string().nullable(), sdk_url: z.string().nullable(),
    price_range_cny: z.string().nullable(), data_formats: z.array(z.string()), evidence: z.array(Evidence),
  }),
});

const hardware = defineCollection({
  loader: file('src/content/generated/hardware.json'),
  schema: z.object({
    id: z.string(), name: z.string(), vram_gb: z.number().nullable(), type: z.string(),
    rental_cny_per_hour_ref: z.number().nullable(), rental_ref_source: z.string().nullable(), rental_ref_url: z.string().nullable(),
    note: z.string().nullable().optional(), evidence: z.array(Evidence),
  }),
});

const compat = defineCollection({
  loader: file('src/content/generated/compat.json'),
  schema: z.object({
    id: z.string(), model_id: z.string(), embodiment_id: z.string(),
    status: z.enum(['official', 'community_verified', 'theoretical', 'unsupported', 'unknown']),
    declared_target_form: z.boolean(), evidence: z.array(Evidence),
  }),
});

const measurements = defineCollection({
  loader: file('src/content/generated/measurements.json'),
  schema: z.object({
    id: z.string(), model_id: z.string(), hardware_id: z.string(), precision: z.string(),
    config: z.object({ batch: z.number(), image_res: z.string(), action_chunk: z.number(), warmup_steps: z.number(), steps: z.number() }),
    metrics: z.object({ latency_ms_p50: z.number(), latency_ms_p95: z.number().nullable(), throughput_chunks_s: z.number().nullable(), vram_peak_gb: z.number().nullable() }),
    source_type: z.enum(['literature', 'maintainer', 'crowd']),
    review_status: z.enum(['pending', 'verified', 'rejected']),
    evidence: z.array(Evidence), created_at: z.string(),
  }),
});

export const collections = { models, embodiments, hardware, compat, measurements };
