# Harwood et al. (2003) - Complete Methodology Reference

## Citation
Harwood, D.W., Rabbani, E.R.K., and Richard, K.R. (2003). "Systemwide optimization of safety improvements for resurfacing, restoration, or rehabilitation projects." Transportation Research Record 1840, pp. 148-157.

---

## 1. OPTIMIZATION FORMULATION

### Objective Function (Equation 4)
```
maximize TB = Σⱼ Σₖ NBⱼₖ × Xⱼₖ
```

Where:
- TB = Total benefits from all selected improvements
- j = site index (1 to y sites)
- k = alternative index at site j (0 to z alternatives)
- Xⱼₖ = Binary decision variable (1 if selected, 0 otherwise)

### Net Benefit Equation (Equation 3)
```
NBⱼₖ = PSBⱼₖ + PTOBⱼₖ + PNRⱼₖ - PRPⱼₖ - CCⱼₖ
```

Where:
- **PSBⱼₖ** = Present value of Safety Benefits (from AMFs)
- **PTOBⱼₖ** = Present value of Traffic Operations Benefits (travel time)
- **PNRⱼₖ** = Penalty for Not Resurfacing (ONLY for do-nothing alternative)
- **PRPⱼₖ** = Penalty for Resurfacing without safety improvements
- **CCⱼₖ** = Construction Cost for alternative k at site j

### Constraints
- **Equations 5-7**: Exactly one alternative per site
  ```
  Σₖ Xⱼₖ = 1  for each site j
  ```

- **Equation 8**: Budget constraint
  ```
  Σⱼ Σₖ CCⱼₖ × Xⱼₖ ≤ B
  ```

---

## 2. SAFETY BENEFIT CALCULATION (PSB)

### Present Value of Safety Benefits (Equation 2)
```
PSBⱼₖ = Σₘ Σₛ Nⱼₘₛ × (1 - AMFₘₖ) × RFₘₛ × ACₛ × (P/A, i, n)
```

Where:
- **m** = Location type index
  - m=1: Non-intersection locations
  - m=2: Intersections
- **s** = Severity level index
  - s=1: Fatal and injury accidents
  - s=2: Property-damage-only (PDO) accidents
- **Nⱼₘₛ** = Expected annual accident frequency for location type m, severity s, at site j
- **AMFₘₖ** = Accident Modification Factor for improvement alternative k at location type m
- **RFₘₛ** = Proportion of total accidents in severity level s (decimal)
- **ACₛ** = Cost savings per accident reduced for severity level s
- **(P/A, i, n)** = Uniform-series present worth factor
  - i = 4% (AASHTO recommended discount rate)
  - n = service life of improvement (typically 20 years)

### AMF Interpretation
- AMF = 1.0 → Base condition (no change)
- AMF < 1.0 → Safety improvement (crashes reduced)
- AMF > 1.0 → Safety degradation (crashes increased)

The **improvement AMF** = AMF_after / AMF_before

---

## 3. CRITICAL NET BENEFIT FORMULA

From the paper (page 153):
> "The net safety benefit is calculated by subtracting the construction cost related to the safety improvements from the total benefits."

### Verification from Table 4 ($50M Budget):
- Safety Benefits (PSB): $9,831,263
- Operations Benefits (PTOB): $809,651
- Total Benefits: $10,640,914
- Safety Improvement Cost: $4,481,397
- **Net Benefit: $10,640,914 - $4,481,397 = $6,159,517** ✓

### Key Insight:
**Resurfacing cost is in the BUDGET CONSTRAINT but NOT subtracted from net benefit.**

Only safety improvement costs are subtracted from benefits in the objective function.

---

## 4. SITE CHARACTERISTICS (Table 1)

| Site | Area | Roadway | Lanes | ADT | Speed | Length | Lane W | Shoulder W | Shoulder Type | Non-Int | Int | Total |
|------|------|---------|-------|-----|-------|--------|--------|------------|---------------|---------|-----|-------|
| 1 | Rural | Undivided | 2 | 1,000 | 35 | 5.2 | 9 | 2 | Turf | 5 | 3 | 8 |
| 2 | Rural | Undivided | 2 | 3,000 | 40 | 4.6 | 10 | 4 | Composite | 4 | 4 | 8 |
| 3 | Rural | Undivided | 2 | 4,000 | 45 | 5.7 | 11 | 4 | Paved | 11 | 11 | 22 |
| 4 | Urban | Divided | 2 | 7,000 | 50 | 2.5 | 10 | 4 | Paved | 15 | 3 | 18 |
| 5 | Rural | Undivided | 4 | 4,000 | 55 | 4.8 | 10 | 4 | Gravel | 10 | 10 | 20 |
| 6 | Urban | Undivided | 4 | 6,000 | 55 | 5.6 | 11 | 6 | Paved | 14 | 14 | 28 |
| 7 | Rural | Divided | 4 | 5,000 | 50 | 5.6 | 11 | 4 | Paved | 13 | 13 | 26 |
| 8 | Rural | Divided | 4 | 10,000 | 50 | 4.5 | 12 | 8 | Paved | 15 | 15 | 30 |
| 9 | Urban | Undivided | 4 | 10,000 | 60 | 3.5 | 10 | 2 | Paved | 12 | 12 | 24 |
| 10 | Urban | Divided | 6 | 15,000 | 60 | 2.3 | 11 | 4 | Paved | 14 | 14 | 28 |

---

## 5. SUMMARY RESULTS (Table 4)

### $50,000,000 Budget (Unconstrained - All Cost-Effective)
| Component | Value |
|-----------|-------|
| Resurfacing Cost | $11,789,849 |
| Safety Improvement Cost | $4,481,397 |
| **Total Cost** | **$16,271,247** |
| Safety Benefits (PSB) | $9,831,263 |
| Operations Benefits (PTOB) | $809,651 |
| **Total Benefits** | **$10,640,914** |
| Penalty for Resurfacing w/o Safety (PRP) | $1,563,278 |
| Penalty for Not Resurfacing (PNR) | $0 |
| **Net Benefit** | **$6,159,517** |

### $10,000,000 Budget (Constrained)
| Component | Value |
|-----------|-------|
| Resurfacing Cost | $7,440,798 |
| Safety Improvement Cost | $2,512,781 |
| **Total Cost** | **$9,953,579** |
| Safety Benefits (PSB) | $6,610,690 |
| Operations Benefits (PTOB) | $577,124 |
| **Total Benefits** | **$7,187,814** |
| PRP | $1,223,009 |
| PNR | $5,576,145 |
| **Net Benefit** | **$4,675,033** |
| **Do-Nothing Sites** | **4, 6, 9** |

---

## 6. IMPROVEMENT TYPES IN RSRAP

The paper considers these improvement types:
1. **Pavement resurfacing** - Default cost calculation
2. **Lane widening** - Default cost calculation
3. **Shoulder widening** - Default cost calculation
4. **Shoulder paving** - Default cost calculation
5. **Horizontal curve improvements** - User-supplied costs
6. **Roadside improvements** - User-supplied costs
7. **Intersection turn lane improvements** - Default cost calculation
8. **User-defined alternatives** - User-supplied costs/benefits

---

## 7. PENALTY TERMS

### Penalty for Not Resurfacing (PNR)
- Applied ONLY to do-nothing alternative (k=0)
- Based on percentage of pavement replacement cost
- Increases as pavement gets closer to failure
- Reflects avoided future reconstruction costs

### Penalty for Resurfacing without Safety Improvements (PRP)
- Applied when resurfacing without geometric improvements
- Based on findings that resurfacing may increase speeds and short-term crashes
- Only applies when lane width < 11 ft OR shoulder width < 6 ft
- User can elect to include or exclude this effect

---

## 8. KEY REFERENCES FOR AMFs

The AMFs used in RSRAP are based on:
1. Zegeer et al. (1987) - Cross section design effects
2. Zegeer et al. (1981) - Lane and shoulder width effects
3. Zegeer et al. (1992) - Horizontal curve improvements
4. Griffin and Mak (1987) - Texas farm-to-market road widening
5. FHWA Technical Advisory T7570.2 - Accident costs

---

## 9. CRITICAL LIMITATION FOR VALIDATION

**The paper only shows the SELECTED alternatives in Tables 2 and 3.**

It does NOT provide:
- Costs and benefits for non-selected alternatives
- The specific AMFs used for each improvement type
- The unit construction costs used

To fully replicate, we would need to:
1. Implement RSRAP's cost calculation methodology
2. Implement RSRAP's AMF-based benefit calculation
3. Calculate costs/benefits for ALL possible alternatives at each site
4. Then run optimization

---

## 10. IMPLEMENTATION NOTES

### For MCBOMs Validation:
1. The $50M case validates the optimizer logic (all sites funded)
2. The $10M case tests budget-constrained selection
3. Must match do-nothing sites: {4, 6, 9}
4. Must match total cost within 5%: $9,953,579
5. Must match net benefit within 5%: $4,675,033

### Discount Rate and Horizon:
- Discount rate: 4% (AASHTO recommendation)
- Analysis horizon: Service life of improvement (typically 20 years)
- Present worth factor (P/A, 4%, 20) = 13.590

---

## 11. FORMULATION SUMMARY FOR CODING

```python
# Objective: Maximize net benefit
# Net Benefit = Total Benefits - Safety Improvement Cost
# where Total Benefits = PSB + PTOB (+ PNR for do-nothing)

objective = sum(
    (total_benefit[j,k] - safety_improvement_cost[j,k]) * x[j,k]
    for j in sites
    for k in alternatives[j]
)

# Budget constraint: Total cost <= Budget
# Total Cost = Resurfacing Cost + Safety Improvement Cost
budget_constraint = sum(
    (resurfacing_cost[j,k] + safety_improvement_cost[j,k]) * x[j,k]
    for j in sites
    for k in alternatives[j]
) <= budget

# Mutual exclusivity: Exactly one alternative per site
for j in sites:
    sum(x[j,k] for k in alternatives[j]) == 1
```

---

*Document created for MCBOMs project validation*
*Texas A&M Transportation Institute*
