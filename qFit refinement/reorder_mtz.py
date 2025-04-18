import gemmi
import numpy as np
import os


def reorder_columns_with_sigfobs(input_mtz_path, output_suffix="_with_sigma"):
    try:
        print(f"\n🔍 Processing file: {input_mtz_path}")

        # Read original MTZ file
        original_mtz = gemmi.read_mtz_file(input_mtz_path)

        # Check required columns
        if not original_mtz.column_with_label("FOBS"):
            raise ValueError("Missing FOBS column")
        if original_mtz.column_with_label("SIGFOBS"):
            print(f"⚠️  File already contains SIGFOBS column. Skipping.")
            return

        # ===== Create new MTZ object =====
        new_mtz = gemmi.Mtz()
        new_mtz.spacegroup = original_mtz.spacegroup
        new_mtz.cell = original_mtz.cell
        new_mtz.title = f"{original_mtz.title} (Processed)"

        # ===== Dataset handling (compatible with new gemmi versions) =====
        if len(original_mtz.datasets) > 0:
            orig_dataset = original_mtz.datasets[0]

            # Add dummy dataset to trigger object creation
            new_dataset = new_mtz.add_dataset("temp_dataset")

            # Manually copy dataset attributes
            new_dataset.project_name = orig_dataset.project_name
            new_dataset.crystal_name = orig_dataset.crystal_name
            new_dataset.dataset_name = orig_dataset.dataset_name

            # Sync dataset ID (critical step)
            if hasattr(orig_dataset, 'id'):
                new_dataset.id = orig_dataset.id

        # ===== Column order handling =====
        target_columns = []
        inserted = False
        for col in original_mtz.columns:
            target_columns.append(col.label)
            if col.label == "FOBS" and not inserted:
                target_columns.append("SIGFOBS")
                inserted = True

        # ===== Add all columns =====
        for label in target_columns:
            if label == "SIGFOBS":
                new_mtz.add_column("SIGFOBS", "Q")
            else:
                orig_col = original_mtz.column_with_label(label)
                new_mtz.add_column(orig_col.label, orig_col.type)

        # ===== Data reorganization =====
        original_data = original_mtz.array
        fobs_idx = original_mtz.column_labels().index("FOBS")
        sigfobs = np.sqrt(np.clip(original_data[:, fobs_idx], 0, None))

        new_data = []
        for label in target_columns:
            if label == "SIGFOBS":
                new_data.append(sigfobs)
            else:
                idx = original_mtz.column_labels().index(label)
                new_data.append(original_data[:, idx])

        new_mtz.set_data(np.column_stack(new_data))

        # ===== Save output file =====
        output_path = f"{os.path.splitext(input_mtz_path)[0]}{output_suffix}.mtz"
        new_mtz.write_to_file(output_path)
        print(f"✅ Successfully generated: {output_path}")

    except Exception as e:
        print(f"❌ Failed to process: {type(e).__name__} - {str(e)}")


if __name__ == "__main__":
    for f in os.listdir('.'):
        if f.endswith('.mtz'):
            reorder_columns_with_sigfobs(f)
    print("\nAll files processed!")
