from __future__ import annotations

from pathlib import Path

from .envcfg import prefix_dir
from .models import RunnerConfig, TargetConfig


def generate_yaml(
    target: TargetConfig,
    prefix_root: Path,
    runner: RunnerConfig,
    wine_version: str,
    proton_version: str,
) -> str:
    target_root = "$GAMEDIR"
    effective_prefix = "$GAMEDIR/pfx" if runner.runner == "proton" else "$GAMEDIR"
    exe = f"{effective_prefix}/drive_c/Program Files/Blackmagic Design/DaVinci Resolve/Resolve.exe"
    include_cuda = target.arch == "x86_64"

    files_lines = [
        '    - resolve_installer: "N/A:Select DaVinci Resolve installer (.exe or .run)"',
        f'    - directml_dll: "N/A:Select directml.dll ({target.arch})"',
    ]
    if include_cuda:
        files_lines.append('    - nvcuda_dll: "N/A:Select nvcuda.dll (x86_64 experimental CUDA)"')

    task_exec_name = "wineexec" if runner.runner == "wine" else "protonexec"
    installer_lines = [
        "    - task:",
        "        name: create_prefix",
        f"        prefix: {target_root}",
        f"        arch: {target.wine_arch}",
        "",
        "    - task:",
        "        name: winetricks",
        f"        prefix: {target_root}",
        "        app: win10 vcrun2019 dx10 dx11",
        "",
        "    - copy:",
        "        src: directml_dll",
        f"        dst: {effective_prefix}/drive_c/windows/system32/directml.dll",
    ]
    if include_cuda:
        installer_lines.extend(
            [
                "",
                "    - copy:",
                "        src: nvcuda_dll",
                f"        dst: {effective_prefix}/drive_c/windows/system32/nvcuda.dll",
            ]
        )
    installer_lines.extend(
        [
            "",
            "    - task:",
            f"        name: {task_exec_name}",
            f"        prefix: {target_root}",
            "        executable: resolve_installer",
            f"        description: Installing {target.display_name}...",
        ]
    )

    reg_lines = [
        "          REGEDIT4",
        "",
        "          [HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]",
        "          \"directml\"=\"native,builtin\"",
    ]
    if include_cuda:
        reg_lines.append("          \"nvcuda\"=\"native,builtin\"")
    reg_lines.extend(
        [
            "",
            "          [HKEY_CURRENT_USER\\Software\\Wine\\Direct3D]",
            "          \"renderer\"=\"vulkan\"",
            "          \"csmt\"=\"enabled\"",
            "          \"VideoMemorySize\"=\"0\"",
            "",
            "          [HKEY_CURRENT_USER\\Control Panel\\Desktop]",
            "          \"LogPixels\"=dword:00000060",
            "",
            "          [HKEY_CURRENT_USER\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers]",
            "          \"C:\\\\Program Files\\\\Blackmagic Design\\\\DaVinci Resolve\\\\Resolve.exe\"=\"~ HIGHDPIAWARE DISABLEDXMAXIMIZEDWINDOWEDMODE\"",
            "",
            "          [HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile]",
            "          \"SystemResponsiveness\"=dword:0000000a",
        ]
    )

    runner_block = [
        "  wine:",
        f"    version: {wine_version}",
        "    esync: true",
        "    fsync: false",
        "    overrides:",
        "      directml: n,b",
    ]
    if include_cuda:
        runner_block.append("      nvcuda: n,b")

    if runner.runner == "proton":
        runner_block = [
            "  proton:",
            f"    version: {proton_version}",
        ]

    yaml_text = "\n".join(
        [
            f"name: {target.display_name} ({runner.runner})",
            f"game_slug: {target.release}",
            f"version: {target.target}",
            f"slug: {target.target}",
            f"runner: {runner.runner}",
            "",
            "script:",
            "  files:",
            *files_lines,
            "",
            "  game:",
            f"    exe: {exe}",
            f"    prefix: {target_root}",
            f"    arch: {target.wine_arch}",
            "    args: \"\"",
            "",
            "  installer:",
            *installer_lines,
            "",
            "    - write_file:",
            "        file: $GAMEDIR/resolve.reg",
            "        content: |",
            *reg_lines,
            "    - task:",
            f"        name: {task_exec_name}",
            f"        prefix: {target_root}",
            "        executable: regedit",
            "        args: /S $GAMEDIR/resolve.reg",
            "",
            *runner_block,
            "",
            "  system:",
            "    env:",
            f"      WINEPREFIX: {effective_prefix}",
            f"      WINEARCH: {target.wine_arch}",
            "      WINEDEBUG: \"-all\"",
            "      WINEESYNC: \"1\"",
            "      __GL_THREADED_OPTIMIZATIONS: \"1\"",
            "      __GL_SHADER_DISK_CACHE: \"1\"",
            "      VK_ICD_FILENAMES: \"/usr/share/vulkan/icd.d\"",
        ]
    )

    if include_cuda:
        yaml_text += "\n      CUDA_EXPERIMENTAL: \"1\""

    return yaml_text + "\n"
