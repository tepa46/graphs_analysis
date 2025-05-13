#include <gunrock/algorithms/pr.hxx>
#include <iostream>

using namespace gunrock;
using namespace memory;

int main(int argc, char **argv) {
	if (argc != 4) {
		std::cerr << "usage: ./bin/<program-name> filename.mtx alpha tol" << std::endl;
		exit(1);
	}

	using vertex_t = int;
	using edge_t = int;
	using weight_t = float;
	using csr_t = format::csr_t<memory_space_t::device, vertex_t, edge_t, weight_t>;

	csr_t csr;

	std::string filename = argv[1];

	if (util::is_market(filename)) {
		io::matrix_market_t <vertex_t, edge_t, weight_t> mm;
		csr.from_coo(mm.load(filename));
	} else {
		std::cerr << "Unknown file format: " << filename << std::endl;
		exit(1);
	}

	weight_t alpha = std::stof(argv[2]);
	weight_t tol = std::stof(argv[3]);

	auto G = graph::build::from_csr<memory_space_t::device, graph::view_t::csr>(
			csr.number_of_rows,
			csr.number_of_columns,
			csr.number_of_nonzeros,
			csr.row_offsets.data().get(),
			csr.column_indices.data().get(),
			csr.nonzero_values.data().get()
	);

	srand(time(NULL));

	vertex_t n_vertices = G.get_number_of_vertices();
	thrust::device_vector <weight_t> p(n_vertices);

	float gpu_elapsed = gunrock::pr::run(G, alpha, tol, p.data().get());
	print::head(p, 8, "First eight ranks");
	return 0;
}