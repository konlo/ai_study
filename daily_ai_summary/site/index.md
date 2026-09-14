---
layout: home
title: AI 뉴스 모아보기
---

AI 관련 최신 기사 5개와 원문 링크를 모읍니다. 요약은 각 출처가 제공한 RSS 설명의 짧은 발췌입니다.

{% assign summaries = site.pages | where_exp: "page", "page.summary_date" | sort: "summary_date" | reverse %}
{% for summary in summaries %}
{% if forloop.first %}
## 최신 요약

[{{ summary.title }}]({{ summary.url | relative_url }})

## 날짜별 기록
{% endif %}
- [{{ summary.summary_date }}]({{ summary.url | relative_url }})
{% endfor %}
