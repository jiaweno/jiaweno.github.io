---
layout: page
title: 标签云
permalink: /tags/
---

{% assign tags = site.tags | sort %}
<div class="tag-cloud">
  {% for tag in tags %}
    <a href="#{{ tag[0] }}" class="tag-link" style="font-size: {{ tag[1].size | times: 4 | plus: 80 }}%">
      {{ tag[0] }}
      <span class="tag-count">({{ tag[1].size }})</span>
    </a>
  {% endfor %}
</div>

<div class="tag-list">
  {% for tag in tags %}
    <h2 id="{{ tag[0] }}">{{ tag[0] }}</h2>
    <ul>
      {% for post in tag[1] %}
        <li>
          <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span>
          <h3>
            <a class="post-link" href="{{ post.url | relative_url }}">
              {{ post.title | escape }}
            </a>
          </h3>
        </li>
      {% endfor %}
    </ul>
  {% endfor %}
</div>

<style>
.tag-cloud {
  margin-bottom: 2rem;
  text-align: center;
}

.tag-link {
  display: inline-block;
  margin: 0.5rem;
  padding: 0.25rem 0.5rem;
  color: #1e88e5;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tag-link:hover {
  background-color: rgba(30, 136, 229, 0.1);
}

.tag-count {
  font-size: 0.8em;
  color: #666;
}

.tag-list h2 {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}
</style> 