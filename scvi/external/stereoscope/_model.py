from scvi.model.base import BaseModelClass
from scvi._compat import Literal

from scvi.external.stereoscope._module import RNADeconv, SpatialDeconv
from anndata import AnnData
from scvi.dataloaders import ScviDataLoader
from scvi.lightning import VAETask
import numpy as np


class RNAStereoscope(BaseModelClass):
    """
    Reimplementation of Stereoscope for deconvolution of spatial transcriptomics from single-cell transcriptomics.
    
    https://github.com/almaan/stereoscope.
    Parameters
    ----------
    sc_adata
        single-cell AnnData object that has been registered via :func:`~scvi.data.setup_anndata`.
    use_cuda
        Use the GPU or not.

    Examples
    --------
    >>> sc_adata = anndata.read_h5ad(path_to_sc_anndata)
    >>> scvi.data.setup_anndata(sc_adata, label_key="labels")
    >>> stereo = scvi.external.stereoscope.RNAStereoscope(sc_adata)
    >>> stereo.train()
    >>> stereo_params = stereo.get_params()
    """

    def __init__(
        self,
        sc_adata: AnnData,
        use_gpu: bool = True,
        **model_kwargs,
    ):
        super(RNAStereoscope, self).__init__(sc_adata, use_gpu=use_gpu)
        self.n_genes = self.summary_stats["n_vars"]
        self.n_labels = self.summary_stats["n_labels"]
        # first we have the scRNA-seq model
        self.model = RNADeconv(
            n_genes=self.n_genes,
            n_labels=self.n_labels,
        )
        self._model_summary_string = (
            "RNADeconv Model with params: \nn_genes: {}, n_labels: {}"
        ).format(
            self.n_genes,
            self.n_labels,
        )
        self.init_params_ = self._get_init_params(locals())

    def get_params(self):
        return self.model.get_params()

    @property
    def _task_class(self):
        return VAETask

    @property
    def _scvi_dl_class(self):
        return ScviDataLoader

class SpatialStereoscope(BaseModelClass):
    """
    Reimplementation of Stereoscope for deconvolution of spatial transcriptomics from single-cell transcriptomics.
    
    https://github.com/almaan/stereoscope.
    Parameters
    ----------
    sc_adata
        single-cell AnnData object that has been registered via :func:`~scvi.data.setup_anndata`.
    use_cuda
        Use the GPU or not.

    Examples
    --------
    >>> st_adata = anndata.read_h5ad(path_to_st_anndata)
    >>> scvi.data.setup_anndata(st_adata)
    >>> st_adata.obs["indices"] = np.arange(st_adata.n_obs)
    >>> register_tensor_from_anndata(st_adata, "ind_x", "obs", "indices")
    >>> stereo = scvi.external.stereoscope.SpatialStereoscope(st_adata, sc_params)
    >>> stereo.train()
    >>> st_adata.obs["deconv"] = stereo.get_proportions()
    """

    def __init__(
        self,
        st_adata: AnnData,
        params: np.ndarray,
        use_gpu: bool = True,
        prior_weight: Literal["n_obs", "minibatch"] = "n_obs",
        **model_kwargs,
    ):
        super().__init__(st_adata, use_gpu=use_gpu)

        self.model = SpatialDeconv(
            n_spots=st_adata.n_obs,
            params=params,
            prior_weight=prior_weight,
            **model_kwargs,
        )
        self._model_summary_string = (
            "RNADeconv Model with params: \nn_spots: {}"
        ).format(
            st_adata.n_obs,
        )
        self.init_params_ = self._get_init_params(locals())

    def get_proportions(self, keep_noise=False):
        return self.model.get_proportions(keep_noise)

    @property
    def _task_class(self):
        return VAETask

    @property
    def _scvi_dl_class(self):
        return ScviDataLoader