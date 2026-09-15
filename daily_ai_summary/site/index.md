---
layout: page
title: AI 뉴스 모아보기
---

국내 매체의 **한국 뉴스 요약**과 해외 매체의 **영문·한국어 요약**을 모읍니다.

[한국 뉴스 출처 목록]({{ "/sources-korea.html" | relative_url }})

{% assign summaries = site.pages | where_exp: "page", "page.summary_date" | sort: "summary_date" | reverse %}
{% assign korean = summaries | where: "edition", "korea" %}
{% assign global = summaries | where: "edition", "global" %}

## 한국 뉴스

{% for summary in korean %}
- [{{ summary.title }}]({{ summary.url | relative_url }}){% if forloop.first %} — 최신{% endif %}
{% endfor %}

## 해외 뉴스 · 한글/영문

{% for summary in global %}
- [{{ summary.title }}]({{ summary.url | relative_url }}){% if forloop.first %} — 최신{% endif %}
{% endfor %}
