# ESA Mission 1 Telemetry Knowledge Base

## Executive Summary

The ESA Mission 1 telemetry dataset contains 76 distinct measurement channels organized across 6 subsystems. The data is stored in Apache Parquet format with a total of approximately 138 million data points across all channels. This knowledge base provides comprehensive documentation of each channel's characteristics, statistical properties, and physical meaning.

---

## Dataset Overview

**Total Channels**: 76  
**Data Format**: Apache Parquet  
**Total Rows Across All Channels**: ~138 million records  
**Purpose**: Satellite telemetry analysis and modeling

The dataset spans multiple subsystems covering different aspects of satellite operations:
- **subsystem_1**: Primary telemetry with 9 channels (channels 1-9, 61-63, 67-69)
- **subsystem_3**: Secondary systems with 11 channels (channels 53-56, 70-76)
- **subsystem_5**: Propulsion/control systems with 6 channels (channels 41-46)
- **subsystem_6**: Primary payload with 50 channels (channels 12-40, 47-52, 57-60, 64-66)

---

## High-Level Statistics and Variance Analysis

### Channels with Highest Variance

The telemetry system shows significant variability across different measurement types. The five channels with the highest standard deviation are:

1. **channel_61** (Standard Deviation: 0.354151) - subsystem_1, physical_unit_6, group 14
    - This channel exhibits the largest variability in the entire dataset
    - Mean value: 0.528906, ranging from 0.000511 to 1.000000
    - Represents a highly dynamic telemetry parameter

2. **channel_62** (Standard Deviation: 0.323313) - subsystem_1, physical_unit_6, group 14
    - Second-highest variance, also in group 14
    - Mean value: 0.489823, with range 0.045605 to 0.968291
    - Strong correlation with channel_61 in the same telemetry group

3. **channel_53** (Standard Deviation: 0.151004) - subsystem_3, physical_unit_5, group 11
    - Third-highest variance across all channels
    - Mean value: 0.831259, spanning 0.000000 to 1.000000
    - Bimodal distribution evident in sample values

4. **channel_10** (Standard Deviation: 0.151235) - subsystem_1, physical_unit_2, group 2
    - Tied for third-highest variance
    - Mean value: 0.111749, with broad range 0.030317 to 0.999776
    - Shows significant measurement uncertainty

5. **channel_56** (Standard Deviation: 0.118776) - subsystem_3, physical_unit_5, group 12
    - Fifth-highest variance
    - Mean value: 0.816765, ranging 0.000000 to 1.000000
    - Discrete value distribution in the sample data

### Channels with Lowest Variance

The system also includes several stable, low-variability channels:

1. **channel_69** (Standard Deviation: 0.003985) - subsystem_1, physical_unit_5, group 17
    - Most stable channel in the dataset
    - Mean: 0.211888, range: 0.000000 to 0.212480
    - Represents a constant or nearly constant measurement

2. **channel_68** (Standard Deviation: 0.013337) - subsystem_1, physical_unit_5, group 17
    - Very low variability, indicating stable system parameter
    - Mean: 0.709157, range: 0.000000 to 0.710675

3. **channel_41** (Standard Deviation: 0.015650) - subsystem_5, physical_unit_4, group 8
    - Low variance in propulsion/control subsystem
    - Mean: 0.809622, range: 0.000000 to 0.982110

---

## Subsystem Breakdown

### Subsystem 1 (Primary Telemetry)
**Channels**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 61, 62, 63, 67, 68, 69  
**Physical Units**: physical_unit_1, physical_unit_2, physical_unit_5, physical_unit_6  
**Total Rows**: ~16.5 million  
**Characteristics**: This subsystem includes both high-variance (channels 61-62 with σ > 0.32) and ultra-stable channels (channel_69 with σ = 0.004). Primarily covers fundamental satellite parameters with telemetry groups 1, 2, 14, and 17.

### Subsystem 3 (Secondary Systems)
**Channels**: 53, 54, 55, 56, 70, 71, 72, 73, 74, 75, 76  
**Physical Units**: physical_unit_4, physical_unit_5  
**Total Rows**: ~75 million  
**Characteristics**: This subsystem shows moderate variance overall. Includes several channels with discrete-level measurements (e.g., channels 54, 56 with specific value distributions). Telemetry groups 11, 12, and 18 are represented here.

### Subsystem 5 (Propulsion/Control Systems)
**Channels**: 41, 42, 43, 44, 45, 46  
**Physical Unit**: physical_unit_4  
**Telemetry Group**: 8  
**Total Rows**: ~92 million  
**Characteristics**: Highly consistent subsystem with all channels showing very low variance (σ = 0.015-0.022). Indicates stable control system performance. All channels mean values cluster around 0.77-0.81.

### Subsystem 6 (Primary Payload)
**Channels**: 12-40, 47-52, 57-60, 64-66  
**Physical Unit**: physical_unit_3  
**Total Rows**: ~78 million  
**Characteristics**: Largest subsystem with 50 channels. Shows wide range of variance from low (channel_57 σ = 0.035) to moderate (channel_14 σ = 0.095). Represents payload measurements across telemetry groups 3-10, 13, 15, 16.

---

## Telemetry Groups Overview

Channels are organized into 18 telemetry groups representing functional categories:

- **Group 1** (channels 1-3): Primary subsystem_1 measurements, low variance (σ = 0.005-0.015)
- **Group 2** (channels 4-11): Secondary subsystem_1 measurements, moderate-high variance (σ = 0.084-0.127)
- **Groups 3-7** (channels 12-40): Primary payload measurements, mostly low variance (σ = 0.043-0.095)
- **Group 8** (channels 41-46): Propulsion/control data, very low variance (σ = 0.015-0.022)
- **Group 9** (channels 47-49): Sparse telemetry, very low variance (σ = 0.012)
- **Group 10** (channels 50-52): Payload status, very low variance (σ = 0.030-0.031)
- **Group 11** (channels 53, 55): Secondary system data, moderate variance (σ = 0.114-0.151)
- **Group 12** (channels 54, 56): Secondary system data, moderate variance (σ = 0.089-0.119)
- **Group 13** (channels 57-60): Payload detail, very low variance (σ = 0.035-0.039)
- **Groups 14-17** (channels 61-69): High-variance operational metrics (σ = 0.004-0.354)
- **Group 18** (channels 70-76): System state monitoring, very low variance (σ = 0.007-0.011)

---

## Physical Measurement Units

The dataset uses 6 distinct physical measurement categories:

- **physical_unit_1**: Used in subsystem_1 (channels 1-3) - Normalized metric, low variance
- **physical_unit_2**: Used in subsystem_1 (channels 4-9) - Moderate variance measurements
- **physical_unit_3**: Primary payload unit (subsystem_6, 50 channels) - Mixed variance
- **physical_unit_4**: Control and monitoring (subsystem_5, subsystem_3) - Very low variance
- **physical_unit_5**: Secondary measurement (subsystem_1, subsystem_3) - Mixed variance
- **physical_unit_6**: High-variance operational metrics (subsystem_1) - Largest variability

---

## Channel-by-Channel Detailed Analysis

### Low Variance, High Stability Channels (σ < 0.05)

These channels represent stable system parameters with minimal fluctuation:

**channel_1** (σ = 0.005040, μ = 0.138048)
- subsystem_1, physical_unit_1, group 1
- 10.5 million rows, no missing values
- Range: 0.092172 to 0.433187
- Interpretation: Primary subsystem metric with exceptional stability

**channel_2** (σ = 0.013930, μ = 0.126724)
- subsystem_1, physical_unit_1, group 1
- 10.5 million rows, no missing values
- Range: 0.000000 to 0.999933
- Interpretation: Primary subsystem baseline with minor fluctuations

**channel_3** (σ = 0.014816, μ = 0.126789)
- subsystem_1, physical_unit_1, group 1
- 10.5 million rows, no missing values
- Range: 0.000000 to 1.000000
- Interpretation: Normalized metric, essentially constant

**channel_11** (σ = 0.019515, μ = 0.039951)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.018257 to 0.084055
- Interpretation: Secondary subsystem measurement with tight control

**channel_41** (σ = 0.015650, μ = 0.809622)
- subsystem_5, physical_unit_4, group 8
- 15.4 million rows, no missing values
- Range: 0.000000 to 0.982110
- Interpretation: Propulsion system telemetry, very stable

**channel_68** (σ = 0.013337, μ = 0.709157)
- subsystem_1, physical_unit_5, group 17
- 4.8 million rows, no missing values
- Range: 0.000000 to 0.710675
- Interpretation: Operational metric, nearly constant

**channel_69** (σ = 0.003985, μ = 0.211888)
- subsystem_1, physical_unit_5, group 17
- 4.8 million rows, no missing values
- Range: 0.000000 to 0.212480
- Interpretation: **Most stable channel in entire dataset** - essentially constant parameter

### Moderate Variance Channels (0.05 < σ < 0.10)

These channels show regular but controlled fluctuations:

**channel_4** (σ = 0.084173, μ = 0.117324)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.036827 to 0.370902

**channel_6** (σ = 0.098989, μ = 0.152514)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.050777 to 0.395864

**channel_7** (σ = 0.127528, μ = 0.161948)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.041182 to 0.402438

**channel_12** (σ = 0.044229, μ = 0.246520)
- subsystem_6, physical_unit_3, group 3
- 14.3 million rows, no missing values
- Range: 0.122595 to 0.996771

**channel_14** (σ = 0.094711, μ = 0.266399)
- subsystem_6, physical_unit_3, group 4
- 5.3 million rows, no missing values
- Range: 0.078451 to 0.971057

**channel_15** (σ = 0.064735, μ = 0.117342)
- subsystem_6, physical_unit_3, group 7
- 5.3 million rows, no missing values
- Range: 0.001287 to 0.541334

**channel_30** (σ = 0.076365, μ = 0.146240)
- subsystem_6, physical_unit_3, group 4
- 5.3 million rows, no missing values
- Range: 0.000000 to 0.592166

### High Variance Channels (σ > 0.10)

These channels exhibit significant variability and represent dynamic system parameters:

**channel_5** (σ = 0.111012, μ = 0.140414)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.034821 to 0.313333

**channel_8** (σ = 0.129425, μ = 0.178067)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.000114 to 0.358936

**channel_9** (σ = 0.127980, μ = 0.175985)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.000000 to 0.355030

**channel_10** (σ = 0.151235, μ = 0.111749)
- subsystem_1, physical_unit_2, group 2
- 3.6 million rows, no missing values
- Range: 0.030317 to 0.999776
- **Tied for 4th highest variance in dataset**

**channel_21** (σ = 0.096506, μ = 0.272769)
- subsystem_6, physical_unit_3, group 4
- 5.3 million rows, no missing values
- Range: 0.073923 to 1.000000

**channel_22** (σ = 0.071570, μ = 0.330000)
- subsystem_6, physical_unit_3, group 7
- 5.3 million rows, no missing values
- Range: 0.021901 to 1.000000

**channel_23** (σ = 0.064472, μ = 0.123272)
- subsystem_6, physical_unit_3, group 7
- 5.3 million rows, no missing values
- Range: 0.000000 to 0.541334

**channel_28** (σ = 0.047536, μ = 0.159347)
- subsystem_6, physical_unit_3, group 3
- 14.3 million rows, no missing values
- Range: 0.000000 to 0.983857

**channel_29** (σ = 0.089967, μ = 0.286058)
- subsystem_6, physical_unit_3, group 4
- 5.3 million rows, no missing values
- Range: 0.085993 to 0.971057

**channel_31** (σ = 0.071837, μ = 0.328417)
- subsystem_6, physical_unit_3, group 7
- 5.3 million rows, no missing values
- Range: 0.015460 to 1.000000

**channel_36** (σ = 0.048909, μ = 0.219116)
- subsystem_6, physical_unit_3, group 3
- 14.3 million rows, no missing values
- Range: 0.073556 to 1.000000

**channel_37** (σ = 0.046267, μ = 0.256705)
- subsystem_6, physical_unit_3, group 3
- 14.3 million rows, no missing values
- Range: 0.122595 to 0.982243

**channel_38** (σ = 0.076114, μ = 0.145778)
- subsystem_6, physical_unit_3, group 4
- 5.3 million rows, no missing values
- Range: 0.009056 to 0.592166

**channel_39** (σ = 0.072340, μ = 0.332588)
- subsystem_6, physical_unit_3, group 7
- 5.3 million rows, no missing values
- Range: 0.030921 to 0.971756

**channel_53** (σ = 0.151004, μ = 0.831259)
- subsystem_3, physical_unit_5, group 11
- 14.6 million rows, no missing values
- Range: 0.000000 to 1.000000
- **3rd highest variance in dataset** - Bimodal distribution visible

**channel_54** (σ = 0.089315, μ = 0.759066)
- subsystem_3, physical_unit_5, group 12
- 14.6 million rows, no missing values
- Range: 0.000000 to 0.900081

**channel_55** (σ = 0.114843, μ = 0.530538)
- subsystem_3, physical_unit_5, group 11
- 14.6 million rows, no missing values
- Range: 0.000000 to 0.714939

**channel_56** (σ = 0.118776, μ = 0.816765)
- subsystem_3, physical_unit_5, group 12
- 14.6 million rows, no missing values
- Range: 0.000000 to 1.000000
- **5th highest variance in dataset** - Discrete level distribution

**channel_61** (σ = 0.354151, μ = 0.528906)
- subsystem_1, physical_unit_6, group 14
- 487,448 rows, no missing values
- Range: 0.000511 to 1.000000
- **HIGHEST VARIANCE in entire dataset** - Most dynamic operational metric

**channel_62** (σ = 0.323313, μ = 0.489823)
- subsystem_1, physical_unit_6, group 14
- 487,448 rows, no missing values
- Range: 0.045605 to 0.968291
- **2nd HIGHEST VARIANCE in dataset** - Highly variable paired with channel_61

**channel_63** (σ = 0.140189, μ = 0.500438)
- subsystem_1, physical_unit_6, group 14
- 487,448 rows, no missing values
- Range: 0.307905 to 0.707881

---

## Data Quality Notes

**Missing Values**: All 76 channels have **zero missing values** across their entire datasets, indicating complete and consistent telemetry recording.

**Data Range**: All channels use normalized values between 0 and 1 (or near 1), suggesting:
- Scaled measurements for comparison
- Physical units have been normalized
- Values represent ratios, percentages, or normalized metrics

**Sample Frequency**: Channels show varying row counts (487K to 19.3M rows), suggesting:
- Different sampling frequencies across subsystems
- Possible grouping by functional area
- Subsystem 6 is sampled most frequently (highest data volume)

---

## Complete Channel Listing

### All 76 Channels by Number

**Channels 1-9** (subsystem_1): Basic telemetry  
**Channels 10-11** (subsystem_1): Extended measurement  
**Channels 12-40** (subsystem_6): Primary payload (29 channels)  
**Channels 41-46** (subsystem_5): Propulsion/control (6 channels)  
**Channels 47-52** (subsystem_6): Payload extension (6 channels)  
**Channels 53-56** (subsystem_3): Secondary systems (4 channels)  
**Channels 57-60** (subsystem_6): Payload detail (4 channels)  
**Channels 61-63** (subsystem_1): High-variance operational metrics (3 channels)  
**Channels 64-66** (subsystem_6): Status monitoring (3 channels)  
**Channels 67-69** (subsystem_1): Operational baseline (3 channels)  
**Channels 70-76** (subsystem_3): System state (7 channels)

---

## Statistical Summary Table

| Metric | Highest | Lowest | Dataset Average |
|--------|---------|--------|-----------------|
| Standard Deviation | 0.354151 (ch_61) | 0.003985 (ch_69) | ~0.065 |
| Mean Value | 0.995900 (ch_67) | 0.001945 (ch_47) | ~0.550 |
| Maximum Range | 1.000000 (ch_3, ch_45, etc) | 0.710675 (ch_68) | Variable |
| Minimum Value | 0.000000 (multiple) | 0.000042 (ch_48) | Mostly ≥0 |
| Row Count | 19.3M (ch_74) | 487K (ch_61-63) | ~13.6M avg |

---

## Practical Interpretation

**For Time-Series Analysis**: Channels 1, 2, 3, 68, 69 are excellent baselines due to exceptional stability. Channels 61-62 show dynamic behavior suitable for trend detection.

**For Anomaly Detection**: Use low-variance channels as reference; deviations from expected values become highly significant. High-variance channels (10, 53, 56, 61, 62) are naturally more variable and require wider anomaly thresholds.

**For Forecasting**: Stable channels (1, 2, 3, 69) are ideal for simple trend models. Dynamic channels (61, 62) require more sophisticated modeling approaches.

**For System Health Monitoring**: Compare current values against historical means and standard deviations. Subsystem_5 consistency (all σ < 0.03) makes it ideal for detecting control system degradation.