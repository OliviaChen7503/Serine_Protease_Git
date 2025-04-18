import gemmi
import numpy as np
import os

def reorder_columns_with_sigfobs(input_mtz_path, output_suffix="_with_sigma"):
    try:
        print(f"\n🔍 开始处理文件: {input_mtz_path}")
        
        # 读取原始MTZ文件
        original_mtz = gemmi.read_mtz_file(input_mtz_path)

        # 检查必要列
        if not original_mtz.column_with_label("FOBS"):
            raise ValueError("缺少 FOBS 列")
        if original_mtz.column_with_label("SIGFOBS"):
            print(f"⚠️  文件已包含 SIGFOBS 列，跳过处理")
            return

        # ===== 创建新MTZ对象 =====
        new_mtz = gemmi.Mtz()
        new_mtz.spacegroup = original_mtz.spacegroup
        new_mtz.cell = original_mtz.cell
        new_mtz.title = f"{original_mtz.title} (Processed)"

        # ===== 数据集处理 (兼容新版gemmi) =====
        if len(original_mtz.datasets) > 0:
            orig_dataset = original_mtz.datasets[0]
            
            # 通过添加空数据集触发对象创建
            new_dataset = new_mtz.add_dataset("temp_dataset")
            
            # 手动复制属性
            new_dataset.project_name = orig_dataset.project_name
            new_dataset.crystal_name = orig_dataset.crystal_name
            new_dataset.dataset_name = orig_dataset.dataset_name
            
            # 同步数据集ID (关键步骤)
            if hasattr(orig_dataset, 'id'):
                new_dataset.id = orig_dataset.id

        # ===== 列顺序处理 =====
        target_columns = []
        inserted = False
        for col in original_mtz.columns:
            target_columns.append(col.label)
            if col.label == "FOBS" and not inserted:
                target_columns.append("SIGFOBS")
                inserted = True

        # ===== 添加所有列 =====
        for label in target_columns:
            if label == "SIGFOBS":
                new_mtz.add_column("SIGFOBS", "Q")
            else:
                orig_col = original_mtz.column_with_label(label)
                new_mtz.add_column(orig_col.label, orig_col.type)

        # ===== 数据重组 =====
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
        
        # ===== 保存文件 =====
        output_path = f"{os.path.splitext(input_mtz_path)[0]}{output_suffix}.mtz"
        new_mtz.write_to_file(output_path)
        print(f"✅ 成功生成: {output_path}")

    except Exception as e:
        print(f"❌ 处理失败: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    for f in os.listdir('.'):
        if f.endswith('.mtz'):
            reorder_columns_with_sigfobs(f)
    print("\n处理完成！")