# Polyglot Persistence Crew Scheduling System

## Overview
This project explores the design of a polyglot persistence architecture to support real-time
crew scheduling, regulatory compliance, and fatigue management for a simulated UK regional airline.

The solution integrates relational, document, and graph databases to address the limitations
of monolithic SQL systems in handling dynamic operational constraints.

## Business Problem
Airlines must comply with strict aviation regulations (CAA CAP 371) while managing
complex crew schedules across time zones. Legacy systems often fail to adapt in real time,
leading to compliance breaches, penalties, and operational inefficiencies.

## Solution Design
The proposed architecture uses:
- MySQL for structured transactional data (crew schedules, duty hours)
- MongoDB for unstructured compliance logs and violation details
- Neo4j for modelling crew–flight–violation relationships and reassignment logic

A Python-based backend (conceptual) orchestrates data validation, compliance checks,
and synchronization across systems.

## Key Analytics & Outcomes
- Automated detection of duty-hour violations
- Improved compliance monitoring and audit readiness
- Simulated reduction in assignment violations and audit preparation effort
- Support for real-time crew reassignment under disruption scenarios

## Deliverables
- Final academic report detailing system design and analysis
- ER diagrams and architecture diagrams
- Sample analytics visualisations (violation distribution, crew role analysis)

## Notes
This project focuses on data architecture, analytics design, and business problem-solving.
While full application code was not developed, the system logic, data flows, and analytical
approach reflect real-world airline operations and compliance requirements.
