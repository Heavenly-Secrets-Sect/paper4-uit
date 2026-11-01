"""Paper 4: dynamic effect estimation under controlled skeleton damage.

Modules follow the experiment steps of the plan (Plan_Paper3_Paper4_Paper5.docx, section 5.2):

- ``topology``  -- load static DAG topologies from the shared generator bank
- ``generator`` -- B1: dynamic SEM (N = 1, i.e. a recursive SVAR) with known truth
- ``skeleton``  -- B3: skeleton in the shared interface format, and controlled damage
- ``estimator`` -- B4: baseline point estimate of the dynamic SEM on a given skeleton
- ``effects``   -- impulse responses, cumulative effect C(H), mean and peak lag
- ``metrics``   -- error of strength and lag against the generator truth
"""
