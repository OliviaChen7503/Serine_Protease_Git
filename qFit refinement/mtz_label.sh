# List of possible amplitude labels to check
obstypes=("FP" "FOBS" "F-obs" "I" "IOBS" "I-obs" "F(+)" "I(+)")

# Extract amplitude fields from metadata
ampfields=$(grep -E "amplitude|intensity|F\(\+\)|I\(\+\)" mtz_metadata.txt | awk '{$1=$1};1' | cut -d " " -f 1)

# Check for valid amplitude and sigma pairs
xray_data_labels=""
for field in ${ampfields}; do
  if [[ " ${obstypes[*]} " =~ " ${field} " ]]; then
    if grep -q -w "SIG${field}" mtz_metadata.txt; then
      xray_data_labels="${field},SIG${field}"
      break
    fi
  fi
done

echo "Detected labels: ${xray_data_labels}"