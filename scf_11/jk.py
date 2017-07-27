import numpy as np
import psi4
try:
    from . import params
except SystemError:
    import params


def make_JK_adv(g, Cocc):
    """
    Function to make the Coulomb and Exchange matrices 
    using density-fitting
    """
# Building the density matrix
    D = Cocc @ Cocc.T

# Building the auxiliary basis
    aux = psi4.core.BasisSet.build(params.mol, fitrole="JKFIT", other="aug-cc-PVDZ")
    
# Building the zero basis for the 2- and 3-center integrals
    zero_bas = psi4.core.BasisSet.zero_ao_basis_set()

# Building mints   
    mints = psi4.core.MintsHelper(params.bas)

# Building 3-center integrals
    Qls_tilde = mints.ao_eri(zero_bas, aux, params.bas, params.bas)
    Qls_tilde = np.squeeze(Qls_tilde)

# Building Coulomb metric
    metric = mints.ao_eri(zero_bas, aux, zero_bas, aux)
    metric.power(-0.5, 1.e-14)
    metric = np.squeeze(metric)

# Building 3-center tensor
    Pls = np.einsum("qls,pq->pls", Qls_tilde, metric)

# Building the Coulomb matrix ( O(N^2*Naux) )
    chi = np.einsum("pls,ls->p", Pls, D)
    J = np.einsum("pmn,p->mn", Pls, chi)

# Building the Exchange matrix ( O(N^2*Naux*p) )
    xi1 = np.einsum("qms,ps->qmp", Pls, Cocc.T)
    xi2 = np.einsum("qnl,pl->qnp", Pls, Cocc.T)
    K = np.einsum("qmp,qnp->mn", xi1, xi2)

    return J, K