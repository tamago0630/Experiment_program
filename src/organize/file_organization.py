from pathlib import Path


WINDOWS_INVALID_MODEL_CHARS = set('<>:"/\\|?*')
WINDOWS_RESERVED_MODEL_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def parse_comma_separated_values(
    raw_input: str,
    field_name: str,
    converter=str,
    sort_values: bool = False,
    validator=None,
) -> list:
    """カンマ区切り入力を変換し、重複を除去して返す。"""
    if not raw_input.strip():
        raise ValueError(f"{field_name} は空文字にできません。")

    values = []
    seen = set()

    for value in raw_input.split(","):
        item = value.strip()
        if not item:
            raise ValueError(f"{field_name} に空の要素を含めることはできません。")
        try:
            converted = converter(item)
        except ValueError as error:
            raise ValueError(f"{field_name} の各要素は正しい形式である必要があります。") from error

        if validator is not None:
            validator(converted)

        if converted not in seen:
            seen.add(converted)
            values.append(converted)

    if sort_values:
        values.sort()

    return values


def validate_model_name(model: str) -> None:
    """Windows でも使用可能な model 名か確認する。"""
    if any(char in WINDOWS_INVALID_MODEL_CHARS for char in model):
        raise ValueError(
            'model に Windows で使用できない文字 (< > : " / \\ | ? *) を含めることはできません。'
        )
    if model.endswith(" ") or model.endswith("."):
        raise ValueError("model はスペースまたはピリオドで終わる名前にできません。")
    if model.upper() in WINDOWS_RESERVED_MODEL_NAMES:
        raise ValueError("model に Windows の予約名は使用できません。")


def create_folder_structure(
    base_dir: str,
    test_method: str,
    models_input: str,
    distances_input: str,
    date: str,
    speed_start: int,
    speed_end: int,
    speed_step: int,
    run_count: int,
) -> Path:
    """実験データ整理用のフォルダ構造を作成する。"""
    # 必須文字列入力が空でないことを確認する
    if not base_dir.strip():
        raise ValueError("base_dir は空文字にできません。")
    if not test_method.strip():
        raise ValueError("test_method は空文字にできません。")

    # 日付が 8 桁の数字であることを確認する
    if not (date.isdigit() and len(date) == 8):
        raise ValueError("date は 8 桁の数字で指定してください。")

    # 速度条件と試行回数の妥当性を確認する
    if speed_step <= 0:
        raise ValueError("speed_step は正の整数である必要があります。")
    if speed_start > speed_end:
        raise ValueError("speed_start は speed_end 以下である必要があります。")
    if run_count < 1:
        raise ValueError("run_count は 1 以上である必要があります。")

    # model と distance を同じ考え方でパースする
    models = parse_comma_separated_values(
        models_input,
        "model",
        validator=validate_model_name,
    )
    try:
        distances = parse_comma_separated_values(
            distances_input,
            "distances",
            converter=int,
            sort_values=True,
        )
    except ValueError as error:
        if "正しい形式" in str(error):
            raise ValueError("distances の各要素は整数である必要があります。") from error
        raise

    base_path = Path(base_dir)
    original_data_path = base_path / "original_data"
    fft_root_path = base_path / "FFT"
    speeds = list(range(speed_start, speed_end + 1, speed_step))

    original_data_path.mkdir(parents=True, exist_ok=True)
    fft_root_path.mkdir(parents=True, exist_ok=True)

    # 作成対象は original_data と FFT のみとする
    for model in models:
        target_roots = (
            original_data_path / model / date,
            fft_root_path / model / date,
        )

        for root_path in target_roots:
            root_path.mkdir(parents=True, exist_ok=True)

            for distance in distances:
                distance_path = root_path / f"R_{distance}"
                distance_path.mkdir(parents=True, exist_ok=True)

                for speed in speeds:
                    speed_path = distance_path / f"{speed}km"
                    speed_path.mkdir(parents=True, exist_ok=True)

    return base_path


if __name__ == "__main__":
    # すべての入力値を input() で受け取り、必要な型へ変換する
    base_dir = input("base_dir: ").strip()
    test_method = input("test_method: ").strip()
    models = input("model: ").strip()
    distances = input("distances: ").strip()
    date = input("date (YYYYMMDD): ").strip()
    speed_start = int(input("speed_start: ").strip())
    speed_end = int(input("speed_end: ").strip())
    speed_step = int(input("speed_step: ").strip())
    run_count = int(input("run_count: ").strip())

    created_root = create_folder_structure(
        base_dir=base_dir,
        test_method=test_method,
        models_input=models,
        distances_input=distances,
        date=date,
        speed_start=speed_start,
        speed_end=speed_end,
        speed_step=speed_step,
        run_count=run_count,
    )

    # 作成した主要パスを分かりやすく表示する
    print(f"作成したベースパス: {created_root}")
    print(f"original_data のパス: {created_root / 'original_data'}")
    print(f"FFT のパス: {created_root / 'FFT'}")
    print("フォルダ構造を作成しました")
