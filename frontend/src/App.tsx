import { useMemo, useState } from "react";
import { api } from "./api";
import type { Candidate, ChatMessage, ScheduleItem, ScheduleResponse } from "./types";

const WEEK_START = "2026-07-13";
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const AREA_ORDER = ["aquatic", "meat", "produce", "cashier", "replenishment"];
const AREA_OPTIONS = [
  { code: "aquatic", name: "水产区" },
  { code: "meat", name: "肉类区" },
  { code: "produce", name: "果蔬区" },
  { code: "cashier", name: "收银/前场" },
  { code: "replenishment", name: "补货区" }
];

function percent(value?: number) {
  return `${Math.round((value ?? 0) * 100)}%`;
}

export function App() {
  const [schedule, setSchedule] = useState<ScheduleResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "我可以解释需求、推荐支援候选人，也可以说明专业师傅为什么不能被抽调。" }
  ]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedArea, setSelectedArea] = useState(AREA_OPTIONS[0].code);

  async function generate() {
    setLoading(true);
    setError("");
    try {
      const response = await api.generateSchedule(WEEK_START);
      setSchedule(response);
      setMessages([{ role: "assistant", content: response.agent_summary }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成失败");
    } finally {
      setLoading(false);
    }
  }

  async function reset() {
    setLoading(true);
    setError("");
    try {
      await api.resetDemo();
      setSchedule(null);
      setCandidates([]);
      setMessages([{ role: "assistant", content: "Demo 数据已重置，可以重新生成班表。" }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "重置失败");
    } finally {
      setLoading(false);
    }
  }

  async function askAgent(question: string) {
    if (!schedule) return;
    setMessages((items) => [...items, { role: "user", content: question }]);
    const friday = schedule.demand_insights.find((item) => item.weekday === "Friday") ?? schedule.demand_insights[0];
    const response = await api.chat(schedule.version_id, question, {
      date: friday?.date,
      slot: friday?.slot ?? "18:00-19:00",
      area_code: friday?.area_code ?? "produce",
      task_code: "restock"
    });
    setMessages((items) => [...items, { role: "assistant", content: response.message }]);
    setCandidates(response.candidates ?? []);
  }

  const groupedByDay = useMemo(() => {
    const rows = new Map<string, ScheduleItem[]>();
    for (const day of DAYS) rows.set(day, []);
    for (const item of schedule?.schedule_items ?? []) {
      if (item.area_code !== selectedArea) continue;
      rows.get(item.weekday)?.push(item);
    }
    for (const items of rows.values()) {
      items.sort((a, b) => {
        const startDiff = slotStartMinutes(a.slot) - slotStartMinutes(b.slot);
        if (startDiff !== 0) return startDiff;
        const typeDiff = employeeTypeOrder(a.employee_type) - employeeTypeOrder(b.employee_type);
        if (typeDiff !== 0) return typeDiff;
        return AREA_ORDER.indexOf(a.area_code) - AREA_ORDER.indexOf(b.area_code) || a.employee_name.localeCompare(b.employee_name, "zh-CN");
      });
    }
    return rows;
  }, [schedule, selectedArea]);

  const selectedAreaName = AREA_OPTIONS.find((area) => area.code === selectedArea)?.name ?? "";

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">社区生鲜示范店 · fresh_store_001</p>
          <h1>智慧排班 Agent</h1>
        </div>
        <div className="toolbar">
          <span className="week-pill">2026-07-13 至 2026-07-19</span>
          <button className="icon-button secondary" onClick={reset} disabled={loading} title="重置 Demo">↺</button>
          <button className="primary-button" onClick={generate} disabled={loading}>
            {loading ? "生成中" : "生成下周半混班班表"}
          </button>
        </div>
      </header>

      {error && <div className="error-strip">{error}</div>}

      <section className="summary-band">
        <Kpi label="专业岗覆盖" value={percent(schedule?.kpis.professional_coverage_rate)} tone="green" />
        <Kpi label="区域保底达成" value={percent(schedule?.kpis.baseline_achievement_rate)} tone="blue" />
        <Kpi label="混排池利用" value={percent(schedule?.kpis.mixed_utilization_rate)} tone="teal" />
        <Kpi label="人工干预率" value={percent(schedule?.kpis.intervention_rate)} tone="gray" />
        <Kpi label="高峰缺口" value={String(schedule?.kpis.peak_gap_count ?? 0)} tone="amber" />
      </section>

      <section className="workbench-grid">
        <aside className="panel area-panel">
          <PanelTitle title="区域保底" />
          <AreaRows schedule={schedule} />
        </aside>

        <section className="panel board-panel">
          <PanelTitle title={`一周班表 · ${selectedAreaName}`} action={schedule?.version_id} />
          <AreaSwitcher selectedArea={selectedArea} onSelect={setSelectedArea} schedule={schedule} />
          {!schedule ? <EmptyState /> : <WeekBoard groupedByDay={groupedByDay} />}
        </section>

        <aside className="panel agent-panel">
          <PanelTitle title="Agent" />
          <div className="quick-row">
            <button onClick={() => askAgent("周五晚高峰果蔬缺人，谁能支援")}>推荐支援</button>
            <button onClick={() => askAgent("为什么不能把老张调去收银")}>不可调解释</button>
            <button onClick={() => askAgent("解释周五晚高峰需求")}>需求解释</button>
          </div>
          <div className="chat-list">
            {messages.map((message, index) => (
              <div key={index} className={`chat-bubble ${message.role}`}>
                {message.content}
              </div>
            ))}
          </div>
          <CandidateList candidates={candidates} />
        </aside>
      </section>

      <section className="bottom-grid">
        <div className="panel">
          <PanelTitle title="需求洞察" />
          <div className="insight-list">
            {(schedule?.demand_insights ?? []).slice(0, 8).map((item) => (
              <div key={`${item.date}-${item.slot}-${item.area_code}`} className="insight-row">
                <strong>{item.area_name}</strong>
                <span>{item.date} {item.slot}</span>
                <meter min={0} max={100} value={item.demand_score} />
                <span>{item.demand_factors.slice(0, 2).join(" / ")}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <PanelTitle title="风险与缺口" />
          <div className="risk-list">
            {(schedule?.risks ?? []).slice(0, 8).map((risk) => (
              <div className="risk-row" key={risk.id}>
                <span className={`risk-dot ${risk.level}`} />
                <p>{risk.description}</p>
              </div>
            ))}
            {!schedule && <p className="muted">生成班表后展示风险。</p>}
          </div>
        </div>
      </section>
    </main>
  );
}

function slotStartMinutes(slot: string) {
  const [hour, minute] = slot.slice(0, 5).split(":").map(Number);
  return hour * 60 + minute;
}

function employeeTypeOrder(type: ScheduleItem["employee_type"]) {
  return type === "regular" ? 0 : 1;
}

function Kpi({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className={`kpi ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function PanelTitle({ title, action }: { title: string; action?: string }) {
  return (
    <div className="panel-title">
      <h2>{title}</h2>
      {action && <code>{action}</code>}
    </div>
  );
}

function AreaRows({ schedule }: { schedule: ScheduleResponse | null }) {
  const rows = useMemo(() => {
    if (!schedule) return [];
    const byArea = new Map<string, { area: string; regular: number; temp: number; protected: number }>();
    for (const item of schedule.schedule_items) {
      const row = byArea.get(item.area_code) ?? { area: item.area_name, regular: 0, temp: 0, protected: 0 };
      if (item.employee_type === "regular") row.regular += 1;
      if (item.employee_type === "temporary") row.temp += 1;
      if (item.is_protected) row.protected += 1;
      byArea.set(item.area_code, row);
    }
    return AREA_ORDER.map((code) => byArea.get(code)).filter(Boolean) as { area: string; regular: number; temp: number; protected: number }[];
  }, [schedule]);

  if (!schedule) return <p className="muted">生成后显示各区域正式工、临时工与专业保护覆盖。</p>;

  return (
    <div className="area-list">
      {rows.map((row) => (
        <div className="area-row" key={row.area}>
          <strong>{row.area}</strong>
          <span>正式工 {row.regular}</span>
          <span>临时 {row.temp}</span>
          <span>保护 {row.protected}</span>
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return <div className="empty-state">点击生成按钮后，这里会展示 7 天半混班班表。</div>;
}

function AreaSwitcher({
  selectedArea,
  onSelect,
  schedule
}: {
  selectedArea: string;
  onSelect: (areaCode: string) => void;
  schedule: ScheduleResponse | null;
}) {
  const counts = useMemo(() => {
    const areaCounts = new Map<string, number>();
    for (const item of schedule?.schedule_items ?? []) {
      areaCounts.set(item.area_code, (areaCounts.get(item.area_code) ?? 0) + 1);
    }
    return areaCounts;
  }, [schedule]);

  return (
    <div className="area-switcher" role="tablist" aria-label="区域排班切换">
      {AREA_OPTIONS.map((area) => (
        <button
          key={area.code}
          type="button"
          role="tab"
          aria-selected={selectedArea === area.code}
          className={selectedArea === area.code ? "active" : ""}
          onClick={() => onSelect(area.code)}
        >
          <span>{area.name}</span>
          <strong>{counts.get(area.code) ?? 0}</strong>
        </button>
      ))}
    </div>
  );
}

function WeekBoard({ groupedByDay }: { groupedByDay: Map<string, ScheduleItem[]> }) {
  return (
    <div className="week-board">
      {DAYS.map((day) => (
        <div className="day-column" key={day}>
          <h3>{day}</h3>
          <div className="assignment-list">
            {(groupedByDay.get(day) ?? []).map((item) => (
              <div className={`assignment ${item.assignment_type}`} key={item.id} title={item.explanation}>
                <span className="assignment-time">{item.slot}</span>
                <strong>{item.employee_name}</strong>
                <span>{item.area_name} · {item.task_name}</span>
              </div>
            ))}
            {(groupedByDay.get(day) ?? []).length === 0 && <p className="muted">本区域当日无排班</p>}
          </div>
        </div>
      ))}
    </div>
  );
}

function CandidateList({ candidates }: { candidates: Candidate[] }) {
  if (!candidates.length) return <p className="muted">候选人会在 Agent 推荐后出现。</p>;
  return (
    <div className="candidate-list">
      {candidates.map((candidate) => (
        <div className="candidate" key={candidate.employee_id}>
          <strong>{candidate.employee_name}</strong>
          <span>技能 {candidate.skill_level} · {candidate.weekly_hours}/{candidate.weekly_hours_limit}h</span>
          <p>{candidate.reason}</p>
        </div>
      ))}
    </div>
  );
}
