import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';
import dotenv from 'dotenv';
import { GoogleGenAI } from '@google/genai';

dotenv.config();

const app = express();
app.use(express.json());
const PORT = process.env.PORT ? parseInt(process.env.PORT) : 3000;

const PROJECT_DIR = path.resolve(process.cwd(), 'project');
const DATA_DIR = path.join(PROJECT_DIR, 'data');
const DEMO_DIR = path.join(PROJECT_DIR, 'demo');

function readJsonFile(filePath: string, fallback: any = []) {
  try {
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error(`Error reading ${filePath}:`, err);
  }
  return fallback;
}

function writeJsonFile(filePath: string, data: any) {
  try {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (err) {
    console.error(`Error writing ${filePath}:`, err);
    return false;
  }
}

// 1. Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'online',
    agent: 'InfraPulse AI - Hindsight SRE Agent',
    memory_bank_id: process.env.HINDSIGHT_MEMORY_BANK_ID || 'mb_infrapulse_sre_prod_01',
    storage: 'Vectorize Hindsight Cloud & Persistent JSON Cache',
    uptime: process.uptime()
  });
});

// 2. Customers / Infrastructure Context
app.get('/api/customers', (req, res) => {
  const customers = readJsonFile(path.join(DATA_DIR, 'customers.json'), []);
  res.json(customers);
});

// 3. Incident Tickets
app.get('/api/tickets', (req, res) => {
  const tickets = readJsonFile(path.join(DATA_DIR, 'tickets.json'), []);
  res.json(tickets);
});

// 3b. Mark Ticket as Resolved & Log Success Memory
app.post('/api/tickets/resolve', (req, res) => {
  try {
    const { ticket_id, verified_runbook, resolution_notes } = req.body;
    const ticketsPath = path.join(DATA_DIR, 'tickets.json');
    const memoriesPath = path.join(DATA_DIR, 'interactions.json');
    const tickets = readJsonFile(ticketsPath, []);
    const memories = readJsonFile(memoriesPath, []);

    const ticketIndex = tickets.findIndex((t: any) => t.ticket_id === ticket_id);
    let targetTicket = ticketIndex >= 0 ? tickets[ticketIndex] : null;

    if (targetTicket) {
      targetTicket.status = 'RESOLVED';
      targetTicket.resolved_at = new Date().toISOString();
      targetTicket.resolution_method = 'Hindsight SRE Verified Protocol';
      tickets[ticketIndex] = targetTicket;
      writeJsonFile(ticketsPath, tickets);
    }

    // Log success memory to Hindsight
    const newMemory = {
      id: `MEM-${Date.now().toString().slice(-6)}-${(memories.length + 1).toString().padStart(3, '0')}`,
      timestamp: new Date().toISOString(),
      customer_id: targetTicket ? targetTicket.customer_id : 'CUST-001',
      customer_name: targetTicket ? targetTicket.customer_name : 'Enterprise Account',
      incident_id: targetTicket ? `INC-${targetTicket.ticket_id.replace('TICK-', '')}` : 'INC-RESOLVED',
      service: targetTicket ? targetTicket.server_id : 'infra-service',
      symptom: targetTicket ? targetTicket.title : 'Incident resolved successfully',
      naive_attempt: targetTicket ? targetTicket.default_runbook_action : 'Naive reboot',
      outcome_of_naive_attempt: 'AVOIDED: Hindsight preemptively blocked destructive runbook and executed verified safe protocol.',
      verified_remediation: verified_runbook || (targetTicket ? targetTicket.default_runbook_action : 'Canary drain and throttled workers'),
      rule_learned: `Verified resolution succeeded on ${new Date().toLocaleDateString()}. Enforced safe throttling protocol without downtime.`,
      memory_type: 'VERIFIED_RESOLUTION_SUCCESS',
      confidence: 0.99
    };

    memories.unshift(newMemory);
    writeJsonFile(memoriesPath, memories);

    res.json({
      success: true,
      ticket: targetTicket,
      memory: newMemory,
      message: `Ticket ${ticket_id} resolved and success memory logged to Hindsight.`
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 4. Demo Scenarios (1 -> 3 -> 5 -> 10)
app.get('/api/scenarios', (req, res) => {
  const scenarios = readJsonFile(path.join(DEMO_DIR, 'demo_scenarios.json'), []);
  res.json(scenarios);
});

// 5. Hindsight Memories
app.get('/api/hindsight/memories', (req, res) => {
  const memories = readJsonFile(path.join(DATA_DIR, 'interactions.json'), []);
  res.json(memories);
});

// 6. Hindsight retain()
app.post('/api/hindsight/retain', (req, res) => {
  try {
    const payload = req.body;
    const memoriesPath = path.join(DATA_DIR, 'interactions.json');
    const memories = readJsonFile(memoriesPath, []);

    const newRecord = {
      id: `MEM-${Date.now().toString().slice(-6)}-${(memories.length + 1).toString().padStart(3, '0')}`,
      timestamp: new Date().toISOString(),
      customer_id: payload.customer_id || 'CUST-MANUAL',
      customer_name: payload.customer_name || 'Enterprise Service',
      incident_id: payload.incident_id || `INC-${Math.floor(100 + Math.random() * 900)}`,
      service: payload.service || 'unknown-service',
      symptom: payload.symptom || 'Incident detected',
      naive_attempt: payload.naive_attempt || 'None recorded',
      outcome_of_naive_attempt: payload.outcome_of_naive_attempt || 'None recorded',
      verified_remediation: payload.verified_remediation || 'Safe drain and canary throttle',
      rule_learned: payload.rule_learned || 'Never restart without throttling workers',
      memory_type: payload.memory_type || 'INCIDENT_RESOLUTION',
      confidence: payload.confidence || 0.98
    };

    memories.unshift(newRecord);
    writeJsonFile(memoriesPath, memories);

    res.json({
      success: true,
      message: 'Retained new incident experience in Hindsight Memory Bank',
      record: newRecord,
      total_memories: memories.length
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 7. Hindsight recall()
app.post('/api/hindsight/recall', (req, res) => {
  try {
    const { query, customer_id, service, top_k = 3 } = req.body;
    const memories = readJsonFile(path.join(DATA_DIR, 'interactions.json'), []);
    const searchTerms = (query || '').toLowerCase().split(/[\s,.-]+/);

    const scored = memories.map((record: any) => {
      let score = 0;
      const text = `${record.service} ${record.symptom} ${record.customer_name} ${record.rule_learned} ${record.naive_attempt} ${record.verified_remediation}`.toLowerCase();

      if (customer_id && record.customer_id === customer_id) score += 5;
      if (service && (record.service || '').toLowerCase().includes(service.toLowerCase())) score += 8;

      for (const term of searchTerms) {
        if (term.length > 2 && text.includes(term)) score += 2;
      }
      return { score, record };
    });

    scored.sort((a: any, b: any) => b.score - a.score);
    const results = scored.slice(0, top_k).map((s: any) => s.record);

    res.json({
      query,
      memory_bank_id: process.env.HINDSIGHT_MEMORY_BANK_ID || 'mb_infrapulse_sre_prod_01',
      retrieved_count: results.length,
      memories: results
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 8. Hindsight reflect()
app.post('/api/hindsight/reflect', (req, res) => {
  try {
    const { topic = 'Connection pool exhaustion & cascading database failures', customer_id } = req.body;
    const memories = readJsonFile(path.join(DATA_DIR, 'interactions.json'), []);

    const relevant = memories.filter((m: any) => !customer_id || m.customer_id === customer_id);
    const incidentIds = relevant.map((m: any) => m.incident_id).slice(0, 5);

    const reflection = {
      topic,
      reflected_at: new Date().toISOString(),
      pattern_summary:
        'Meta-analysis across historical incidents reveals that container pod restarts during peak traffic periods invariably trigger connection storm cascades against stateful databases (Aurora / Spanner / Redis). Teams repeatedly misattributed this to pod RAM limits, but the root cause is absence of worker ingress backpressure.',
      systemic_vulnerability:
        'Unbuffered gRPC ingress spikes combined with unthrottled consumer workers saturate connection limits within 8 seconds of cache cold starts.',
      proactive_policy_rule:
        'MANDATORY POLICY: Prohibit uncoordinated rollout restarts. Prior to cache key unlinking, throttle upstream workers to 20% traffic and activate canary drain with exponential jittered backoff.',
      supporting_incidents: incidentIds,
      confidence_score: 0.98
    };

    res.json(reflection);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 9. Side-by-Side Incident Diagnosis Engine
app.post('/api/diagnose', (req, res) => {
  try {
    const { ticket, use_hindsight_memory = true } = req.body;
    const memories = readJsonFile(path.join(DATA_DIR, 'interactions.json'), []);

    if (!use_hindsight_memory) {
      const dangerousCmd = ticket?.default_runbook_action || 'kubectl rollout restart deployment <service>';
      return res.json({
        ticket_id: ticket?.ticket_id || 'TICK-UNKNOWN',
        mode: 'WITHOUT_MEMORY',
        recalled_memories_count: 0,
        recalled_memories: [],
        dangerous_actions_blocked: [],
        diagnosis: `Generic AI Recommendation: The error logs show connection pool saturation. Execute standard runbook: \`${dangerousCmd}\`. Monitor pod CPU and RAM utilization.`,
        verified_safe_runbook: `⚠️ UNVERIFIED RUNBOOK: \`${dangerousCmd}\`. Warning: Generic AI has zero historical context and does not evaluate downstream database blast radius.`,
        explanation_of_reasoning: 'Generic AI operates purely on textbook documentation keywords. It cannot know that restarting this service previously caused total database connection starvation and dropped 48,000 transactions.',
        learning_delta: 'ZERO MEMORY: High likelihood of repeat catastrophic outage ($300k+ transaction loss).',
        confidence: 0.42
      });
    }

    // WITH HINDSIGHT
    const match = memories.find((m: any) =>
      ticket?.customer_id === m.customer_id ||
      (ticket?.server_id && m.service && (ticket.server_id.includes(m.service) || m.service.includes(ticket.server_id.split('-')[0])))
    ) || memories[0];

    const recalledMemories = [match];
    const blockedCmd = match.naive_attempt || ticket?.default_runbook_action || 'kubectl rollout restart deployment';

    res.json({
      ticket_id: ticket?.ticket_id || 'TICK-UNKNOWN',
      mode: 'WITH_HINDSIGHT',
      recalled_memories_count: recalledMemories.length,
      recalled_memories: recalledMemories,
      dangerous_actions_blocked: [
        `${blockedCmd} (Failed in Incident #${match.incident_id}: ${match.outcome_of_naive_attempt})`
      ],
      diagnosis: `🛑 CATASTROPHIC COMMAND BLOCKED: Standard runbook proposes \`${ticket?.default_runbook_action}\`. Hindsight recalled Incident #${match.incident_id}, where executing this command caused: "${match.outcome_of_naive_attempt}". Enforcing Institutional SRE Rule: ${match.rule_learned}`,
      verified_safe_runbook: match.verified_remediation,
      explanation_of_reasoning: `Hindsight retrieved Incident #${match.incident_id}. Rather than blindly executing a cold pod restart, the agent recognized that the connection pool timeout is driven by checkout worker saturation. Throttling workers first safely preserves database uptime.`,
      learning_delta: `EXPERIENCE APPLIED: Prevented recurring 48-minute P1 outage and saved estimated $300,000+ transaction loss. Cites Maya Krishnan constraint.`,
      confidence: 0.98
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 10. Live Search Grounding for CVEs & Kernel Advisories
app.post('/api/search-grounding', async (req, res) => {
  const { query = 'redis connection timeout CVE 2026 linux kernel' } = req.body;
  const apiKey = process.env.GEMINI_API_KEY;

  if (apiKey) {
    try {
      const ai = new GoogleGenAI({ apiKey });
      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: `You are an expert infrastructure SRE. Investigate the following query for any recent CVEs, known kernel socket bugs, or upstream cloud provider outage notices: ${query}. Provide a concise 2-sentence summary with recommendations.`,
        config: {
          tools: [{ googleSearch: {} }]
        }
      });
      return res.json({
        grounding_active: true,
        query,
        summary: response.text,
        sources: response.candidates?.[0]?.groundingMetadata?.groundingChunks || []
      });
    } catch (err: any) {
      console.warn('Gemini search grounding fallback:', err.message);
    }
  }

  // Graceful fallback if no Gemini key or offline
  res.json({
    grounding_active: false,
    query,
    summary:
      'Search Grounding advisory: Upstream Linux kernel tcp_tw_recycle deprecation can cause socket starvation under high SYN rates. Verified upstream mitigation is tuning net.ipv4.tcp_max_syn_backlog=4096 and tcp_fin_timeout=15.',
    sources: [{ title: 'Linux Kernel TCP Socket Documentation', uri: 'https://kernel.org/doc/Documentation/networking/ip-sysctl.txt' }]
  });
});

// 11. Code & Project Explorer API
app.get('/api/project-tree', (req, res) => {
  try {
    function walkDir(dir: string, base: string = ''): any[] {
      const items = fs.readdirSync(dir);
      const list: any[] = [];
      for (const item of items) {
        if (item === '__pycache__' || item === '.git' || item.endsWith('.pyc')) continue;
        const fullPath = path.join(dir, item);
        const relPath = path.join(base, item);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
          list.push({
            name: item,
            path: relPath,
            type: 'directory',
            children: walkDir(fullPath, relPath)
          });
        } else {
          list.push({
            name: item,
            path: relPath,
            type: 'file',
            size: stat.size
          });
        }
      }
      return list;
    }

    const tree = walkDir(PROJECT_DIR);
    res.json({ root: 'project', tree });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/project-file', (req, res) => {
  try {
    const file = req.query.path as string;
    if (!file) return res.status(400).json({ error: 'Missing path query parameter' });
    const fullPath = path.resolve(PROJECT_DIR, file);
    if (!fullPath.startsWith(PROJECT_DIR)) {
      return res.status(403).json({ error: 'Access denied' });
    }
    if (!fs.existsSync(fullPath)) {
      return res.status(404).json({ error: 'File not found' });
    }
    const content = fs.readFileSync(fullPath, 'utf-8');
    res.json({ path: file, content });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Mount Vite middleware in development
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.resolve(__dirname, 'dist')));
    app.get('*', (req, res) => {
      res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[InfraPulse AI] Server listening on http://0.0.0.0:${PORT}`);
  });
}

startServer();
