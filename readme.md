# Mids Cost Estimator

Estimate the total cost of fully slotted City of Heroes character builds exported from Mids Reborn, using up-to-date Auction House prices.

## Features

- **Estimates total influence cost** for a Mids `.mbd` build file, using a detailed price list.
- **Breaks down costs** by enhancement type and quantity.
- **Warns about unknown enhancements** and uses a fallback price for them.
- **Customizable price list** via `prices.yaml`.

## Requirements

- Python 3.7+
- [PyYAML](https://pyyaml.org/) (`pip install pyyaml`)

## Usage

```sh
python mids_cost_estimator.py <path_to_build.mbd>
```

Example:

```sh
python mids_cost_estimator.py my_blaster.mbd
```

## Output

- Build name, level, and class (from the `.mbd` file)
- Total number of enhancements
- Cost breakdown by enhancement type (sorted by total cost)
- Total estimated cost in millions of influence
- List of unknown enhancements (if any)

## File Descriptions

### `mids_cost_estimator.py`

The main script. It:
- Loads enhancement prices from `prices.yaml`
- Loads a Mids `.mbd` build file (JSON format)
- Extracts all slotted enhancements
- Calculates and prints the cost breakdown

### `prices.yaml`

A YAML file with estimated Auction House prices (in millions of influence) for each enhancement, organized by category. You can update this file as market prices change.

**Example structure:**
```yaml
defaults:
  superior_attuned: 9.0
  attuned: 4.0
  # ... more defaults ...
superior_attuned:
  Superior_Attuned_Superior_Defiant_Barrage_A:
  Superior_Attuned_Superior_Defiant_Barrage_B:
  # ... more ...
attuned:
  Attuned_Overwhelming_Force_F:
# ... more categories ...
```

If an enhancement is not listed, the script uses the default for its category, or a fallback of 1.05 million.

### `.mbd` File Format

The script expects a Mids Reborn build file in JSON format. The relevant structure is:

```json
{
  "Name": "My Blaster",
  "Level": 50,
  "Class": "Blaster",
  "PowerEntries": [
    {
      "SlotEntries": [
        {
          "Enhancement": {
            "Uid": "Superior_Attuned_Superior_Defiant_Barrage_A",
            "IoLevel": 50
          }
        }
        // ... more slots ...
      ]
    }
    // ... more powers ...
  ]
}
```

- Only the `Uid` field is used for price lookup.
- If `IoLevel` is missing, 50 is assumed.

## Notes

- If `prices.yaml` is missing, the script will warn and use fallback prices.
- Unknown enhancements are listed at the end of the output.

## License

MIT
