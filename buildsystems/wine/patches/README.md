# resolve-wine Patches

Place `*.patch` files in this directory.

They are applied in lexical order before build.
Recommended patch domains for DaVinci Resolve:
- timer precision and scheduler behavior
- synchronization/contention hot paths
- PE loader edge cases
- rawinput/HID stability
- large-address and memory mapping behavior
