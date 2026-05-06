from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re


SKILLS_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    description: str
    triggers: tuple[str, ...]
    body: str


def _parse_front_matter(raw_text: str) -> tuple[dict[str, str], str]:
    if not raw_text.startswith("---\n"):
        return {}, raw_text.strip()

    closing_marker = raw_text.find("\n---\n", 4)
    if closing_marker == -1:
        return {}, raw_text.strip()

    front_matter = raw_text[4:closing_marker]
    body = raw_text[closing_marker + 5 :].strip()
    parsed: dict[str, str] = {}

    description_match = re.search(
        r"(?ms)^description:\s*\|\n(?P<value>(?:^[ \t].*\n?)*)",
        front_matter,
    )
    if description_match:
        parsed["description"] = "\n".join(
            line.strip() for line in description_match.group("value").splitlines()
        ).strip()

    cleaned_front_matter = re.sub(
        r"(?ms)^description:\s*\|\n(?:^[ \t].*\n?)*",
        "",
        front_matter,
    )

    for line in cleaned_front_matter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")

    return parsed, body


def _extract_triggers(
    raw_text: str, metadata: dict[str, str], body: str, skill_dir_name: str
) -> tuple[str, ...]:
    candidates: list[str] = []

    explicit_triggers = metadata.get("triggers", "").strip()
    if explicit_triggers:
        candidates.extend(part.strip() for part in explicit_triggers.split(","))

    search_space = "\n".join(
        part for part in (metadata.get("description", ""), body, raw_text) if part
    )
    trigger_match = re.search(r"触发词[：:]\s*(.+)", search_space)
    if trigger_match:
        trigger_text = trigger_match.group(1)
        candidates.extend(re.findall(r"[「\"']([^」\"']+)[」\"']", trigger_text))

    candidates.extend([metadata.get("name", "").strip(), skill_dir_name.strip()])

    deduped: list[str] = []
    for candidate in candidates:
        normalized = candidate.strip()
        if not normalized or normalized in deduped:
            continue
        deduped.append(normalized)

    return tuple(deduped)


@lru_cache(maxsize=1)
def load_skills() -> list[Skill]:
    skills: list[Skill] = []

    for skill_path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        raw_text = skill_path.read_text(encoding="utf-8").strip()
        metadata, body = _parse_front_matter(raw_text)

        name = metadata.get("name") or skill_path.parent.name
        description = metadata.get("description", "")
        triggers = _extract_triggers(raw_text, metadata, body, skill_path.parent.name)

        skills.append(
            Skill(
                name=name,
                path=skill_path,
                description=description,
                triggers=triggers,
                body=body,
            )
        )

    return skills


def get_active_skills(user_input: str) -> list[Skill]:
    normalized_input = user_input.strip()
    if not normalized_input:
        return []

    lowered_input = normalized_input.lower()
    active_skills: list[Skill] = []

    for skill in load_skills():
        for trigger in skill.triggers:
            normalized_trigger = trigger.strip()
            if not normalized_trigger:
                continue

            if (
                normalized_trigger in normalized_input
                or normalized_trigger.lower() in lowered_input
            ):
                active_skills.append(skill)
                break

    return active_skills


def build_skills_prompt(user_input: str) -> str:
    skills = get_active_skills(user_input)
    if not skills:
        return ""

    sections = [
        "当前用户输入命中了以下本地 Skill，请严格按对应 Skill 的角色、约束、风格和禁忌回答。",
        "如果 Skill 与通用助手职责冲突，以安全和事实准确为先；未命中的 Skill 不要启用。",
    ]

    for skill in skills:
        summary = skill.description or "无描述"
        sections.append(
            f"\n[Skill: {skill.name}]\n"
            f"文件: {skill.path.as_posix()}\n"
            f"触发词: {', '.join(skill.triggers)}\n"
            f"描述: {summary}\n"
            f"内容:\n{skill.body}"
        )

    return "\n".join(sections).strip()
