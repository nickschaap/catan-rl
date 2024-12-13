# Purchase Power

Purchase power is a heuristic for determining how well settled a player is to make certain purchases. It builds off their resource abundance. The purchase power for a settlement is the summation of the resource abundance of WOOD, BRICK, SHEEP, and WHEAT. The purchase power for a city is the summation of ORE / 3, WHEAT / 2. The result is divided by the total number of resources needed to make that purchase.

## Red

```
Purchase Power:
PieceType.SETTLEMENT: 0.12
PieceType.CITY: 0.04083333333333333
PieceType.ROAD: 0.17
Development Card: 0.07333333333333335
```

## Blue

```
Purchase Power:
PieceType.SETTLEMENT: 0.125
PieceType.CITY: 0.03
PieceType.ROAD: 0.125
Development Card: 0.10333333333333333
```

## Orange

```
Purchase Power:
PieceType.SETTLEMENT: 0.12250000000000001
PieceType.CITY: 0.065
PieceType.ROAD: 0.095
Development Card: 0.12000000000000001
```

## White

```
Purchase Power:
PieceType.SETTLEMENT: 0.1
PieceType.CITY: 0.030833333333333334
PieceType.ROAD: 0.13
Development Card: 0.09333333333333334
```
