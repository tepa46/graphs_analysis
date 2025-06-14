#include "ssbfs.hxx"

#include <filesystem>

using namespace gunrock;
using namespace memory;

int main(int argc, char **argv) {
	if (argc != 3) {
		std::cerr << "usage: ./bin/<program-name> filename.mtx single_source" << std::endl;
		exit(1);
	}

	using vertex_t = int;
	using edge_t = int;
	using weight_t = float;
	using csr_t = format::csr_t<memory_space_t::device, vertex_t, edge_t, weight_t>;

	csr_t csr;
	std::string filename = argv[1];
	std::string filename_stem = std::filesystem::path(filename).stem().string();

	if (util::is_market(filename)) {
		io::matrix_market_t<vertex_t, edge_t, weight_t> mm;
		csr.from_coo(mm.load(filename));
	} else {
		std::cerr << "Unknown file format: " << filename << std::endl;
		exit(1);
	}

	vertex_t single_source = std::stoi(argv[2]);

	thrust::device_vector<vertex_t> row_indices(csr.number_of_nonzeros);
	thrust::device_vector<vertex_t> column_indices(csr.number_of_nonzeros);
	thrust::device_vector<edge_t> column_offsets(csr.number_of_columns + 1);

	auto G = graph::build::from_csr<memory_space_t::device, graph::view_t::csr>(
			csr.number_of_rows, csr.number_of_columns, csr.number_of_nonzeros, csr.row_offsets.data().get(),
			csr.column_indices.data().get(), csr.nonzero_values.data().get(), row_indices.data().get(),
			column_offsets.data().get());

	vertex_t n_vertices = G.get_number_of_vertices();
	thrust::device_vector<vertex_t> distances(n_vertices);
	thrust::device_vector<vertex_t> predecessors(n_vertices);

	float gpu_elapsed = gunrock::bfs::run(G, single_source, distances.data().get(), predecessors.data().get());

	std::cout << filename_stem << " SSBFS " << single_source << " elapsed time: " << gpu_elapsed << " (ms)" << std::endl;
}