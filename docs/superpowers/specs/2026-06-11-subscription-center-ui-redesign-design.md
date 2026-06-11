# Subscription Center UI Redesign Design

## Goal

Redesign the ttlink subscription center into a personal ops workspace that belongs to the existing TTLINK Ops Console system. The page should feel like a black personal-site portal with a usable subscription operations window, not like a generic SaaS dashboard.

The primary user need is to quickly understand subscription usage activity: which IPs are using the subscription, when they were last seen, where they appear to be from, which node they use, and how much traffic they used. Copying the active subscription must remain immediately available, but the full subscription URL should not be visually exposed by default.

## Scope

In scope:

- Redesign `/subscribe` as a Subscription Workspace.
- Integrate `/subscribe` conceptually with `/about` as part of TTLINK Ops Console.
- Add or refine a Subscription Center entry from `/about` to `/subscribe`.
- Preserve existing mock-driven data for the first implementation.
- Adjust the mock data shape where needed for IP details and future real log integration.
- Keep the page desktop-first while maintaining mobile usability.

Out of scope for this design:

- Building a real backend log ingestion pipeline.
- Adding authentication to this Astro page.
- Changing the real subscription URL or YAML distribution path.
- Removing existing ops documentation content.
- Replacing the `/about` console with a full single-page app.

## Design Read

Reading this as: personal infra workspace for one operator, with a black personal-site portal language, leaning toward native Astro and CSS with a restrained monochrome starlight aesthetic.

Design dials:

- Design variance: 6. Centered personal identity at the top, structured data windows below.
- Motion intensity: 2. Mostly static, with hover, focus, copy feedback, and optional smooth anchor scrolling.
- Visual density: 7. Dense enough for ops work, but grouped into readable windows with clear breathing space.

## Chosen Approach

Use the **Console homepage plus Subscription Workspace** approach.

- `/about` remains the TTLINK Ops Console hub.
- `/subscribe` becomes a dedicated Subscription Workspace.
- `/about` should expose a Subscription Center module that links into `/subscribe` and optionally offers a quick copy action.
- `/subscribe` carries the detailed subscription operations experience.

This avoids overloading `/about` while still making the subscription center feel like part of the same personal ops system.

## Visual Direction

The final direction is **monochrome starlight ops**.

Key traits:

- Near-black background.
- Fine grid or subtle starfield texture inspired by old black-and-white QQ Zone non-mainstream decoration.
- A small number of silver-white star glints, not a heavy decorative background.
- Centered TTLINK identity at the top.
- Monospace subtitle such as `STDIN | Subscribe >> /ops/workspace`.
- White and gray typography with very limited color.
- White soft glow for current navigation and active rows.
- No colorful orb, neon gradient, large chromatic avatar, or dashboard-like color system.

The page should feel artistic through space, grid, star glints, centered identity, and restrained light, not through many colors.

## Page Structure

### 1. Console Identity Header

Top section:

- Centered title: `TTLINK`.
- Monospace subtitle: `STDIN | Subscribe >> /ops/workspace`.
- Black grid or sparse starlight background.
- No large colorful avatar.

### 2. Portal-Style Anchor Navigation

Keep five icon entries as a personal-site-style directory, but implement them as anchor navigation, not tabs.

Entries:

- Subscription
- IP Activity
- Nodes
- Traffic
- Docs

Behavior:

- Clicking an entry scrolls to the matching section.
- Content is not hidden or swapped.
- Default highlight is on Subscription because this is the subscription workspace entry point.
- Highlight uses white or gray-white soft light, not blue, green, purple, or gradient color.

### 3. Subscription Action Panel

A compact floating panel under the navigation.

Content:

- Active subscription label.
- Online or available status.
- Last updated timestamp.
- Text indicating that the URL is hidden.
- Copy subscription button.
- Open YAML button.

Rules:

- Do not show the full subscription URL by default.
- Do not place Back to Console inside this panel.
- Copy feedback must be textual, such as `Copied` or `Failed`.
- The panel is an action area, not a navigation area.

### 4. IP Activity Window

This is the primary content area.

Desktop layout:

- Largest data window on the page.
- Table-like layout with fixed-height scroll window.
- Rows sorted by last seen time.
- The most recent row may receive a subtle white left-edge highlight.

Recommended columns:

- IP / device label.
- Location / ISP.
- Last seen.
- Today usage.
- Node.

Additional details to support in data:

- ASN.
- First seen today.
- Session count.
- Trust level or note.
- Optional source such as local, mobile, remote, unknown.

Mobile layout:

- Convert rows to stacked activity cards.
- Avoid horizontal overflow.
- Keep copy/open subscription actions at the top.

### 5. Node Health Panel

Right-side supporting panel on desktop.

Content:

- HY2 primary node.
- VLESS fallback node.
- Status.
- Latency.
- Protocol.
- Route role.

Visual treatment:

- Compact status list, not large equal cards.
- Use typography and spacing for hierarchy.
- Avoid colorful node badges unless needed for semantic warnings.

### 6. Traffic Summary Panel

Traffic is supporting information, not the page focus.

Content:

- Today usage.
- Month-to-date usage.
- Seven-day trend.
- Optional per-node usage.

Important constraint:

- Do not show traffic budget or quota, because the Aliyun server does not have a meaningful traffic cap for this use case.
- Do not render a large traffic budget card.

### 7. Operations Docs

Keep existing docs content, but move it below the main first-screen workspace.

Docs include:

- Subscription import.
- Node switching.
- Ops checks.
- Architecture notes.

Presentation can remain tabs or become collapsible sections. It should not compete with IP activity for first-screen priority.

## Data Model

The first implementation can continue to use static mock data from `src/data/subscription.ts`, with adjustments for clearer future API boundaries.

### subscriptionOverview

Keep:

- title.
- subtitle.
- planName.
- subscriptionUrl.
- lastUpdated.
- todayTrafficGb.
- activeNodes.
- totalNodes.
- uniqueIpsToday.
- uniqueIpsMonth.

Change:

- Do not use `totalTrafficGb` as a visual quota in the UI.
- If kept for compatibility, treat it as unused by the redesigned visual layer.

Add if useful:

- status, such as `online`, `checking`, `unavailable`, `misconfigured`.
- urlVisibilityLabel, such as `URL hidden`.

### ipStats

Existing fields should be expanded.

Recommended fields:

- ip.
- label.
- location.
- isp.
- asn.
- lastSeen.
- firstSeenToday.
- sessionCount.
- today.
- month.
- node.
- trustLevel.
- note.

The IP activity window is the core future backend integration point.

### proxyNodes

Keep current structure, with optional display refinements:

- name.
- role.
- roleLabel.
- domain.
- protocol.
- route.
- status.
- latency.
- usage.
- description.

### trafficBars

Keep as simple trend data.

Use only for lightweight visual context.

### opsDocs

Keep current content and IDs.

Move lower in page hierarchy.

## States

Design these states even if first implementation uses static mock data.

### Subscription

- online: copy and open actions enabled.
- checking: show subtle skeleton text or `checking` status.
- unavailable: copy/open disabled with clear message.
- misconfigured: show configuration warning.

### Copy action

- idle: button says copy subscription.
- copied: temporary copied state.
- failed: temporary failed state.

### IP activity

- populated: scroll window with records.
- empty: clear empty state, such as no IP usage records yet.
- loading: skeleton rows matching final row shape.
- error: message such as unable to read usage logs, while subscription actions remain available if known.

### Node health

- online.
- degraded.
- offline.
- unknown.

## `/about` Integration

Add or refine a Subscription Center module on `/about`.

The module should:

- Link to `/subscribe`.
- Show concise status: online, active nodes, recent IP count, last update.
- Optionally offer a quick copy action.
- Match the ops console language but does not need to duplicate the full starlight visual system.

Avoid embedding the whole IP table into `/about`.

## Accessibility and Interaction

Requirements:

- Buttons need visible focus states.
- Anchor navigation must use real links or buttons with accessible labels.
- Copy feedback must use visible text, not color alone.
- The IP table/window should have semantic labeling.
- Text contrast must remain high on the black background.
- Motion should respect reduced motion.
- Smooth scrolling is optional and must not be the only way to navigate.

## Responsive Behavior

Desktop-first layout:

- Centered identity and anchor navigation.
- Subscription action panel centered below navigation.
- Main grid: IP activity window left, node and traffic panels right.

Mobile layout:

- Header remains centered but smaller.
- Anchor navigation can wrap or become horizontal scroll.
- Subscription action panel stacks actions.
- IP table becomes activity cards.
- Node and traffic panels stack below.
- Docs appear after main panels.

## Visual Guardrails

Do:

- Use monochrome starlight and subtle grid.
- Use white and gray hierarchy.
- Use sparse star glints.
- Keep the IP window readable.
- Keep the URL hidden by default.

Do not:

- Add a colorful orb or colorful avatar.
- Use neon gradients.
- Use many status colors.
- Turn the anchor navigation into content-switching tabs.
- Make traffic quota the main visual object.
- Show the full subscription URL as a large block.
- Put Back to Console inside the subscription action panel.

## Testing and Verification

Implementation should be verified with:

1. `npm run build`.
2. Manual browser check of `/about` and `/subscribe`.
3. Copy button check that the hidden real subscription URL is copied.
4. Open YAML check that it navigates to the real URL.
5. Desktop visual check against the approved v6 direction.
6. Mobile check for no horizontal overflow.
7. Accessibility spot check for focus, labels, and contrast.

## Open Implementation Notes

- Use native Astro and CSS first. Avoid adding a design system dependency for this redesign.
- Existing symbols in the visual companion are design-only glyphs. Implementation may use text symbols or CSS-styled simple glyphs. Do not introduce a large icon library unless the plan justifies it.
- The background starlight should be CSS-based and lightweight.
- The `.superpowers/brainstorm` mockups are design references only and should not be treated as production code.
