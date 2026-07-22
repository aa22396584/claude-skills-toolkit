# Flutter performance checklist

## Build, layout, and rebuilds

- Broad `setState`, provider, Riverpod, Bloc, inherited-widget, or stream updates.
- Repeated object creation or transformations inside `build`.
- `shrinkWrap: true` on large/dynamic lists.
- `SingleChildScrollView` plus a large eager `Column`.
- `IntrinsicHeight` or `IntrinsicWidth` in repeated children.
- Missing item extent/prototype where rows are predictably sized.
- Custom layout delegates that trigger unnecessary relayout.

## Raster and compositing

- Large/frequent blur, `BackdropFilter`, shader masks, save layers, opacity groups,
  anti-aliased clips with save layers, or large shadows.
- Animating complex static subtrees without an intentional repaint boundary.
- Excessive repaint boundaries that create layer/memory overhead.
- Large custom painters repainting when their inputs are unchanged.
- Full-screen transparency/overdraw and expensive clipping.

## Images and memory

- Source images decoded far larger than rendered dimensions.
- Unbounded pre-cache, long image lists, animated images, or repeated cache eviction.
- Full byte copies between isolate/plugin/native layers.
- Controllers, listeners, subscriptions, focus nodes, or animations not disposed.
- Large in-memory JSON/object graphs retained across screens.

## Dart and I/O

- JSON decode, sorting, grouping, compression, cryptography, PDF/image work, or
  database migrations on a latency-sensitive isolate.
- Chatty platform channels or serial network waterfalls.
- Duplicate requests caused by rebuilds or lifecycle callbacks.
- Work moved to isolates without accounting for startup and transfer cost.

## Platform Views

- Map, WebView, camera, ads, or native player under animated Flutter overlays.
- Clip, opacity, transform, or frequent resize around native views.
- Multiple simultaneous native views in a scrollable surface.

## Startup and size

- Sequential initialization before first frame.
- Eager analytics, database, remote config, or dependency graph construction.
- Large native libraries, duplicate ABIs/assets/fonts, and unused resources.

Each checklist match still requires focused source review and, where practical,
runtime verification.
